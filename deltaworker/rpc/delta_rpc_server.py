import pandas as pd
from deltalake.writer import write_deltalake
import glob2
import os
import duckdb
import asyncio
import concurrent.futures
import json

import asyncio
import aiormq
import aiormq.abc

conn = duckdb.connect(':memory:')

# For error handling
def create_error_response(code, message, error_type=None):
    response = {
        "status": "error",
        "code": code,
        "message": message,
    }
    if error_type:
        response["error_type"] = error_type
    return response
    
# Ingest Data by scraping directory for csvs
# Endpoint equivalent for /ingestdata
async def ingestdata(request_json):
    async def read_and_process_csv(file):
        # Read and process CSV asynchronously
        df = await asyncio.to_thread(pd.read_csv, file)
        df = df.astype(str)
        return df
    
    try:
        data = request_json['request_args']
        
        # Use DuckDB to query from all csv files in specified directory
        dirpath = os.path.join(f'data/raw/{data["request_folderpath"]}/', "*.csv")
        # DeltaTables need Pandas DataFrames that are all in string
        duck_query = f"SELECT * FROM read_csv_auto('{dirpath}', all_varchar = true)"
        combined_df = conn.execute(duck_query).fetchdf()

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
        response = create_error_response(500, "Internal server error")
        return json.dumps(response, indent=4)

# Set up endpoint dictionary
endpoints = {
    "ingestdata": ingestdata
}
    
# RPC Code
async def on_message(message: aiormq.abc.DeliveredMessage):
    request_json = json.loads(message.body.decode())
    
    # Set up API Style routing to "endpoints":
    raw_response = await endpoints[request_json["request_endpoint"]](request_json)
        
    response = raw_response.encode()

    await message.channel.basic_publish(
        response,
        routing_key=message.header.properties.reply_to,
        properties=aiormq.spec.Basic.Properties(
            content_type='application/json',
            correlation_id=message.header.properties.correlation_id,
        ),
    )

    await message.channel.basic_ack(message.delivery.delivery_tag)
    print('Request complete')


async def main():
    # Perform connection
    connection = await aiormq.connect("amqp://guest:guest@rabbitmq/")

    # Creating a channel
    channel = await connection.channel()

    # Declaring queue
    declare_ok = await channel.queue_declare('delta_rpc')

    # Start listening to the queue
    await channel.basic_consume(declare_ok.queue, on_message)


loop = asyncio.get_event_loop()
loop.create_task(main())

# we enter a never-ending loop that waits for data
# and runs callbacks whenever necessary.
print(" [x] Awaiting RPC requests")
loop.run_forever()