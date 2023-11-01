from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import requests
import json

import numpy as np
import pandas as pd

from make_response import create_json_responses  # Update with the correct module name


app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        message_data = json.loads(message)
        message_requestfrom = message_data.get('request_from')
        message_requestcontents = message_data.get('request_contents')

        if message_requestfrom == 'duck':
            # Create a sample dataframe with random values
            num_rows = 7  # For example, 7 days in a week
            num_columns = 4  # For example, 3 datasets
            data = np.random.randint(0, 100, (num_rows, num_columns))
            df = pd.DataFrame(data, columns=['Data One', 'Data Two', 'Data Three', 'Data Four'])
            df.index = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

            json_response = create_json_responses(df,message_requestcontents)

            # Send the JSON chart data
            await websocket.send_text(json_response)