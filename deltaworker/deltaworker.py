from fastapi import FastAPI, WebSocket, HTTPException, Request
import pandas as pd
from deltalake.writer import write_deltalake
import glob2
import os
import duckdb
import asyncio
import concurrent.futures
import json

app = FastAPI()

conn = duckdb.connect(':memory:')
    
@app.get("/ingestdata")
async def ingestdata(request: Request):
    async def read_and_process_csv(file):
        # Read and process CSV asynchronously
        df = await asyncio.to_thread(pd.read_csv, file)
        df = df.astype(str)
        return df
    try:
        data = await request.json()

        # Use asyncio.gather to read and process CSV files in parallel
        csv_files = glob2.glob(os.path.join(f'data/raw/{data["request_folderpath"]}/', "*.csv"))
        processed_data = await asyncio.gather(*(read_and_process_csv(file) for file in csv_files))

        # Combine the processed data
        combined_df = pd.concat(processed_data)

        # Asynchronously write to DeltaLake storage
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, lambda: write_deltalake(f'data/deltalake/{data["request_tablename"]}', combined_df, mode=data["request_method"]))

        json_response = {
            "respond_to": "delta",
            "response_contents": ["message"],
            "data": {
                "message": "DeltaLake stored as " + data["request_tablename"]
            }
        }
        return json.dumps(json_response, indent=4)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))