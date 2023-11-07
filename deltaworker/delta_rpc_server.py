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
    
#@app.get("/ingestdata")
async def ingestdata(request_json):
    async def read_and_process_csv(file):
        # Read and process CSV asynchronously
        df = await asyncio.to_thread(pd.read_csv, file)
        df = df.astype(str)
        return df
    data = request_json['request_args']

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
    
    
# RPC Code
async def on_message(message: aiormq.abc.DeliveredMessage):
    request_json = json.loads(message.body.decode())
    
    # Set up API Style routing to "endpoints":
    if request_json["request_endpoint"] == "ingestdata":
        raw_response = await ingestdata(request_json)
        
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

    # Start listening the queue with name 'hello'
    await channel.basic_consume(declare_ok.queue, on_message)


loop = asyncio.get_event_loop()
loop.create_task(main())

# we enter a never-ending loop that waits for data
# and runs callbacks whenever necessary.
print(" [x] Awaiting RPC requests")
loop.run_forever()