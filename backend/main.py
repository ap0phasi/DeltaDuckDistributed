from fastapi import FastAPI, WebSocket, HTTPException
import asyncio
import uuid
import aiormq
import aiormq.abc
import json

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
            routing_key=json.loads(request_json).get('request_to')+'_rpc',
            properties=aiormq.spec.Basic.Properties(
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )

        response_json = await future
        return json.loads(response_json.decode())
    
# Make request
async def make_request(message_json):
    backend_rpc = await BackendRpcClient().connect()
    response = await backend_rpc.call(message_json)
    return response

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
        message_json = json.loads(message_text)
        json_response = await backend_rpc.call(json.dumps(message_json))
        # # Send the JSON chart data
        # json_response = {
        #     "respond_to": "delta",
        #     "response_contents": ["message"],
        #     "data": {
        #         "message": "Hello"
        #     }
        # }
        json_response = json.dumps(json_response, indent=4)
        await websocket.send_text(json_response)