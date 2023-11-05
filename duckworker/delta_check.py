import os
import duckdb
import re

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

def log_tables(path, connection):
    # Ensure the provided path is a directory
    if not os.path.isdir(path):
        print(f"The path {path} is not a directory.")
        return

    # Create a cursor object using the connection
    cursor = connection.cursor()

    # Ensure the table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS __deltalake_dir (
        TableName VARCHAR,
        Parent VARCHAR,
        Query VARCHAR
    )
    """)

    # List all entries in the directory and add or update them in the DuckDB table
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        # Check if it is a directory
        if os.path.isdir(full_path):
            # Delete existing rows with the same TableName and Parent (which is NULL in this case)
            cursor.execute("""
                DELETE FROM __deltalake_dir
                WHERE TableName = ? AND Parent IS NULL
            """, ("=(^)" + entry,))
            
            # Now that any potential conflicts have been removed, insert the new row
            cursor.execute("""
                INSERT INTO __deltalake_dir (TableName, Parent, Query)
                VALUES (?, ?, ?)
            """, ("=(^)" + entry, None, None))

    # Commit the transaction
    connection.commit()
    print("Directories have been upserted into the database.")
    
# Function to extract table names from a SQL query
def extract_tables(sql,connection):
    # Parse the SQL query
    parsed = sqlparse.parse(sql)[0]
    
    # This will store the results
    new_table = None
    source_tables = []
    
    # Track whether a CREATE TABLE operation was found
    create_table_found = False
    create_table_populated = False

    # Iterate over the tokens in the parsed query
    for item in parsed.tokens:
        # If the token is a DML operation and it is 'CREATE'
        if item.value.upper() == 'CREATE':
            create_table_found = True
        
        # If a CREATE TABLE operation was previously found and the token is an Identifier
        if create_table_found and isinstance(item, Identifier):
            new_table = item.get_real_name()
            create_table_populated = True
            create_table_found = False
            
        # If the created table is found assume everything else is source
        elif create_table_populated and isinstance(item, Identifier):
            source_tables.append(item.get_real_name())
            create_table_populated = True
    if new_table is not None:
        write_table_log(sql,new_table,source_tables,connection)
    
    return "Parsed"

def write_table_log(query,new_table,source_tables,connection):
    cursor = connection.cursor()
    for source_table in source_tables:
        cursor.execute("""
            INSERT INTO __deltalake_dir (TableName, Parent, Query)
            VALUES (?, ?, ?)
        """, (new_table, source_table, query))
    

if __name__=="__main__":
    # Example usage:
    # Establish a connection to the DuckDB database
    conn = duckdb.connect(':memory:')

    # Create a cursor object using the connection
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS __deltalake_dir (
        TableName VARCHAR,
        Parent VARCHAR,
        Query VARCHAR
    )
    """)
    # Call the function with the path to the directory and the connection
    #log_tables('data/deltalake', conn)
    
    # Your SQL command
    sql_command = "CREATE TABLE IF NOT EXISTS tabletemp1 AS SELECT * FROM =(^)someother"
    # Extract the table names
    extract_tables(sql_command,conn)
    
    conn.close()
