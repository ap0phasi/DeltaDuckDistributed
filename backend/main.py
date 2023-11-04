from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json

import numpy as np
import pandas as pd
import aiohttp

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
        try:
            # Receive message
            message = await websocket.receive_text()
            message_data = json.loads(message)
            message_requestto = message_data.get('request_to')
            message_requestendpoint = message_data.get('request_endpoint')

            # Attempt to send the request and get a response
            json_response = await send_request(
                urls[message_requestto][0] + message_requestendpoint,
                json=message_data.get('request_args')
            )

            # Send the JSON chart data
            await websocket.send_text(json_response)

        except json.JSONDecodeError:
            # Handle JSON decode error (e.g., bad JSON in message)
            await websocket.send_text(json.dumps({'error': 'Invalid JSON format.'}))
        
        except KeyError:
            # Handle missing fields in message_data
            await websocket.send_text(json.dumps({'error': 'Missing required fields in the message.'}))
        
        except HTTPException as e:
            # Handle HTTP exceptions from send_request
            if e.status_code == 400:
                await websocket.send_text(json.dumps({'error': 'Bad request: ' + str(e.detail)}))
            else:
                # You can add more specific error handling for other HTTP status codes if needed
                await websocket.send_text(json.dumps({'error': 'An error occurred: ' + str(e.detail)}))
        
        except Exception as e:
            # Handle any other exceptions that may occur
            await websocket.send_text(json.dumps({'error': 'An unexpected error occurred: ' + str(e)}))