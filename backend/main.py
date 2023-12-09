from fastapi import FastAPI, WebSocket, HTTPException
import asyncio
import uuid
import aiormq
import aiormq.abc
import json
import aiohttp
import os

import numpy as np
import pandas as pd

from parse_queries import parse_and_create_packets

app = FastAPI()

#RPC Client
class BackendRpcClient:
    def __init__(self):
        self.connection = None      # type: aiormq.Connection
        self.channel = None         # type: aiormq.Channel
        self.callback_queue = ''
        self.futures = {}
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        # When running in Containers use the name of the rabbitmq service as in docker-compose
        self.connection = await aiormq.connect("amqp://guest:guest@rabbitmq/")

        self.channel = await self.connection.channel()
        declare_ok = await self.channel.queue_declare(
            exclusive=True, auto_delete=True
        )

        await self.channel.basic_consume(declare_ok.queue, self.on_response)

        self.callback_queue = declare_ok.queue

        return self

    async def on_response(self, message: aiormq.abc.DeliveredMessage):
        future = self.futures.pop(message.header.properties.correlation_id)
        future.set_result(message.body)

    async def call(self, request_json):
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.basic_publish(
            request_json.encode(),
            # Different workers are looking at different queues, we write to the appropiate queue here
            routing_key=json.loads(request_json).get('request_to')+'_rpc', # If there was a node specified, 'request_to' would include it
            properties=aiormq.spec.Basic.Properties(
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )

        response_json = await future
        return response_json.decode()
    
# Make request to RPC
async def make_request(message_json):
    backend_rpc = await BackendRpcClient().connect()
    response = await backend_rpc.call(message_json)
    return response

# Make request to API
async def send_request(url, params = None, json = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params = params, json = json) as resp:
            response = await resp.json()
            return response
        
# Set API URLS
url_routes = {
    "delta" : "http://deltaworker:8002/",
    "duck" : "http://duckworker:8003/"
}

# Get whatever worker type was specified in docker-compose. 
delta_worker_type = os.getenv('delta_worker_type')
duck_worker_type = os.getenv('duck_worker_type')
# Set message routes
message_routes = {
    "delta" : delta_worker_type,
    "duck" : duck_worker_type
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    backend_rpc = BackendRpcClient()
    await backend_rpc.connect()

    while True:
        message_text = await websocket.receive_text()
        message_json = json.loads(message_text)

        try:
            if message_routes[message_json.get('request_to')] == "rpc":
                # Check if request_args contains 'request_query' and that 'request_query' contains '-- id:'
                request_args = message_json.get('request_args', {})
                request_query = request_args.get('request_query', '')
                if request_query and '-- id: ' in request_query:
                    query_text = message_json['request_args']['request_query']
                    packets, nodes = parse_and_create_packets(query_text)\
                        
                    for packet, node in zip(packets, nodes):
                        tasks = []
                        for query, query_node in zip(packet, node):
                            # Create a copy of the message_json for each query
                            message_to_send = message_json.copy()  
                            message_to_send['request_args'] = message_to_send.get('request_args', {}).copy()

                            # Update 'request_to' with node information if available
                            if query_node:
                                message_to_send['request_to'] = message_to_send['request_to'] + query_node

                            # Update the 'request_query'
                            message_to_send['request_args']['request_query'] = query

                            # Create an asyncio task for the query
                            tasks.append(asyncio.create_task(backend_rpc.call(json.dumps(message_to_send))))
                        
                        # Wait for all tasks in the packet to complete
                        responses = await asyncio.gather(*tasks)
                        for response in responses:
                            await websocket.send_text(response)

                else:
                    # Process as a single request if no 'request_query' field or if no decorator
                    response_message = await backend_rpc.call(message_text)
                    await websocket.send_text(response_message)
                    
            elif message_routes[message_json.get('request_to')] == "api":
                message_requestto = message_json.get('request_to')
                message_requestendpoint = message_json.get('request_endpoint')
                # Attempt to send the request and get a response
                json_response = await send_request(
                    url_routes[message_requestto] + message_requestendpoint,
                    json=message_json.get('request_args')
                )
                # Send the JSON response data
                await websocket.send_text(json_response)

        except Exception as e:
            await websocket.send_text(json.dumps({'error': 'An unexpected error occurred: ' + str(e)}))
