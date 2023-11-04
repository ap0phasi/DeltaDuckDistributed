from fastapi import FastAPI, WebSocket, HTTPException, Request
import pandas as pd
import duckdb
import re
from deltalake import DeltaTable
from make_response import create_json_responses
import json


app = FastAPI()

conn = duckdb.connect(':memory:')

@app.get("/querydata")
async def querydata(request: Request):
    data = await request.json()
    print(data)
    query_result = await process_duck_query(conn,data['request_query'], data['request_contents'], data['request_render'])
    return json.dumps(query_result, indent=4)


async def process_duck_query(conn, sql_query, request_contents, render_size):
    pattern = r'=\(\^\)(\w+)'
    matches = re.findall(pattern, sql_query)
    delta_tables = []
    
    delta_path = "data/deltalake/"

    for match in matches:
        delta_tables.append(match)

    deltasets = {}
    new_sql_query = sql_query
    for delta_table in delta_tables:
        dt = DeltaTable(delta_path + delta_table)
        pyarrow_dataset = dt.to_pyarrow_dataset()
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