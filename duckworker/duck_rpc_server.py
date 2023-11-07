import asyncio
import aiormq
import aiormq.abc

import pandas as pd
import duckdb
import re
from deltalake import DeltaTable
from make_response import create_json_responses
from delta_check import log_tables, extract_tables
import json
import numpy as np

# Establish functions for different tasks on this worker.
# These are reused from the FastAPI without the API decorator.
# The old API connection is used for reference to route functions

# Default to in-memory duckdb connection
conn = duckdb.connect(':memory:')

# Check what delta lakes exist
#@app.get("/checktable")
async def checktable(request_json):
    log_tables('data/deltalake', conn)
    json_response = {
        "respond_to": "delta",
        "response_contents": ["message"],
        "data": {
            "message": "_directory_list updated"
        }
    }
    return json.dumps(json_response, indent=4)

# Allow user to request duckdb connection
#@app.get("/duckconnect")
async def duckconnect(request_json):
    data = request_json['request_args']
    global conn 
    conn = duckdb.connect(data['conn_string'])
    json_response = {
        "respond_to": "settings",
        "response_contents": ["message"],
        "data": {
            "message": "Connected!"
        }
    }
    
    return json.dumps(json_response, indent=4)
#Perform data querying
#@app.get("/querydata")
async def querydata(request_json):
    data = request_json['request_args']
    if data['request_query'] == "=(^)quack":
        # Create a sample dataframe with random values
        num_rows = data['request_render']  # For example, 7 days in a week
        num_columns = 3  # For example, 3 datasets
        df = pd.DataFrame(np.random.randint(0,100,size=(num_rows, num_columns)), columns=['Data One', 'Data Two', 'Data Three'])

        query_result = create_json_responses(df, data['request_contents'])
    else:
        query_result = await process_duck_query(conn,data['request_query'], data['request_contents'], data['request_render'])
    
    # Once query is successful add the record to our table log
    extract_tables(data['request_query'], conn)
    
    return json.dumps(query_result, indent=4)

async def process_duck_query(conn, sql_query, request_contents, render_size):
    # Extract all user specified DeltaTables
    pattern = r'=\(\^\)(\w+)'
    matches = re.findall(pattern, sql_query)
    delta_tables = []
    
    delta_path = "data/deltalake/"

    for match in matches:
        delta_tables.append(match)

    # Each DeltaTable specified by the user will need to be loaded as a DuckDB dataset
    new_sql_query = sql_query
    for delta_table in delta_tables:
        # First connect to the DeltaTable in the data path
        dt = DeltaTable(delta_path + delta_table)
        # Create a pyarrow dataset from the DeltaTable
        pyarrow_dataset = dt.to_pyarrow_dataset()
        # Convert the pyarrow dataset to a DuckDB dataset to make it queryable
        locals()[delta_table] = duckdb.arrow(pyarrow_dataset)
        new_sql_query = new_sql_query.replace(f'=(^){delta_table}', delta_table)
    chunk_size = 1_000_000
    
    tostream = conn.execute(new_sql_query).fetch_record_batch(chunk_size)

    num_rows, num_columns , pandas_chunk = await streamer_step(tostream,render_size)
    json_response = create_json_responses(pandas_chunk, request_contents)
    json_response['data']['message'] = f"Queried Result Size: {str(num_rows)}, {str(num_columns)}"
    return json_response

async def streamer_step(to_stream, render_size):
    num_rows = 0
    num_columns = len(to_stream.schema)  # Get the number of columns from the schema
    while True:
        try:
            chunk = to_stream.read_next_batch()
            num_rows += len(chunk)  # Increment the row count for each chunk
        except StopIteration:
            break
    pandas_chunk = chunk.slice(length = render_size + 1).to_pandas()
    return num_rows, num_columns , pandas_chunk


# RPC Code
async def on_message(message: aiormq.abc.DeliveredMessage):
    print("RECEVIED MESSAGE")
    request_json = json.loads(message.body.decode())
    
    # Set up API Style routing to "endpoints":
    if request_json["request_endpoint"] == "checktable":
        raw_response = await checktable(request_json)
    elif request_json["request_endpoint"] == "duckconnect":
        raw_response = await duckconnect(request_json)
    elif request_json["request_endpoint"] == "querydata":
        raw_response = await querydata(request_json)
        
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
    declare_ok = await channel.queue_declare('duck_rpc')

    # Start listening the queue with name 'hello'
    await channel.basic_consume(declare_ok.queue, on_message)


loop = asyncio.get_event_loop()
loop.create_task(main())

# we enter a never-ending loop that waits for data
# and runs callbacks whenever necessary.
print(" [x] Awaiting RPC requests")
loop.run_forever()