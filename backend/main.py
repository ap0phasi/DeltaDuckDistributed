from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import requests
import json

import numpy as np
import pandas as pd

from make_response import dataframe_to_json_chart  # Update with the correct module name


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

            # Convert the dataframe to JSON chart format
            json_chart = dataframe_to_json_chart(df)

            # Send the JSON chart data
            await websocket.send_text(json_chart)