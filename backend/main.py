from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import requests
import json

import numpy as np
import pandas as pd
import aiohttp

from make_response import create_json_responses 

urls = {
    "delta" : ["http://deltaworker:8002/"],
    "duck" : ["http://duckworker:8003/"]
}

app = FastAPI()

async def send_request(url, params = None, json = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params = params, json = json) as resp:
            response = await resp.json()
            return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        message_data = json.loads(message)
        message_requestfrom = message_data.get('request_from')
        message_requestendpoint = message_data.get('request_endpoint')

        json_response = await send_request(urls[message_requestfrom][0]+message_requestendpoint, json=message_data.get('request_args'))
        # Send the JSON chart data
        await websocket.send_text(json_response)