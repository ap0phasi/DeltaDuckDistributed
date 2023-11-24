from fastapi import FastAPI, WebSocket, HTTPException, Request
import pandas as pd
from deltalake.writer import write_deltalake
import glob2
import os
import duckdb
import asyncio
import concurrent.futures
import json
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import re

app = FastAPI()

conn = duckdb.connect(':memory:')
# Postgres Connection
def connect_postgres():
    conn.execute("ATTACH 'dbname=postgres_db user=user password=password host=postgres' AS postgres (TYPE postgres)")
    
def refresh_postgres():
    conn.execute("DETACH postgres")
    connect_postgres()

# Initial postgres connection
connect_postgres()
    
@app.get("/ingestdata")
async def ingestdata(request: Request):
    try:
        data = await request.json()
        # Refresh connection with Postgres, only if postgres is mentioned
        if "postgres" in data['request_folderpath']:
                refresh_postgres()
                
        # If the folder path provided appears to be a query, solve it directly
        input_is_query = "SELECT" in data['request_folderpath']
        if input_is_query:
            duck_query = data['request_folderpath']
        else:
            # Use DuckDB to query from all csv files in specified directory
            dirpath = os.path.join(f'data/raw/{data["request_folderpath"]}/', "*.csv")
            # DeltaTables need Pandas DataFrames that are all in string
            duck_query = f"SELECT * FROM read_csv_auto('{dirpath}')"
        combined_df = conn.execute(duck_query).fetch_arrow_table()

        # Asynchronously write to DeltaLake storage
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, lambda: write_deltalake(f'data/deltalake/{data["request_tablename"]}', combined_df, large_dtypes=True, mode=data["request_method"]))
        
        # If input was a query then we want to update our tracker accordingly
        if input_is_query:
            # Parse the SQL query for tables:
            parsed = sqlparse.parse(duck_query)[0]
            # Iterate over the tokens in the parsed query
            for item in parsed.tokens:
                if isinstance(item, Identifier):
                    # Handle =(^)convention
                    itemname = item.value
                    pattern = r'\(\^\)(\w+)'
                    if bool(re.search(pattern,itemname)):
                        itemname = "=" + itemname

                    # Insert into tracking table
                    keysearch = conn.execute("SELECT MAX(t_id) FROM postgres.__deltalake_dir").fetchdf().iloc[0,0]
                    keyval = 0 if keysearch != keysearch else keysearch + 1 
                    conn.execute("""
                            INSERT INTO postgres.__deltalake_dir (t_id, TableName, Parent, Query)
                            VALUES (?, ?, ?, ?)
                        """, (str(keyval), "=(^)" + data["request_tablename"], itemname, data['request_folderpath']))
                    
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