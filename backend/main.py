from fastapi import FastAPI, WebSocket, HTTPException
import asyncio
import uuid
import aiormq
import aiormq.abc
import json
import aiohttp

import numpy as np
import pandas as pd

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
            routing_key=json.loads(request_json).get('request_to')+'_rpc',
            properties=aiormq.spec.Basic.Properties(
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )

        response_json = await future
        return json.loads(response_json.decode())
    
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

# Set message routes
message_routes = {
    "delta" : "rpc",
    "duck" : "rpc"
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Instantiate the RPC client once and connect it.
    backend_rpc = BackendRpcClient()
    await backend_rpc.connect()
    # Ensure that backend_rpc is properly instantiated.
    while True:
        # Receive message
        message_text = await websocket.receive_text()
        # Extract JSON
        message_json = json.loads(message_text)
        
        if message_routes[message_json.get('request_to')] == "rpc":
            # Call RPC and await response
            response_message = await backend_rpc.call(json.dumps(message_json))
            # I am confused why I need to dump the json, shouldn't the response already be that?
            json_response = json.dumps(response_message, indent=4)
            await websocket.send_text(json_response)
            
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