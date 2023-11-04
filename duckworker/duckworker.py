from fastapi import FastAPI, WebSocket, HTTPException, Request
import pandas as pd
import duckdb
import re
from deltalake import DeltaTable
from make_response import create_json_responses
import json
import numpy as np

app = FastAPI()

# Default to in-memory duckdb connection
conn = duckdb.connect(':memory:')

# Allow user to request duckdb connection
@app.get("/duckconnect")
async def querydata(request: Request):
    try:
        data = await request.json()
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
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/querydata")
async def querydata(request: Request):
    try:
        data = await request.json()
        if data['request_query'] == "=(^)quack":
            # Create a sample dataframe with random values
            num_rows = data['request_render']  # For example, 7 days in a week
            num_columns = 3  # For example, 3 datasets
            df = pd.DataFrame(np.random.randint(0,100,size=(num_rows, num_columns)), columns=['Data One', 'Data Two', 'Data Three'])

            query_result = create_json_responses(df, data['request_contents'])
        else:
            query_result = await process_duck_query(conn,data['request_query'], data['request_contents'], data['request_render'])
            
        return json.dumps(query_result, indent=4)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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