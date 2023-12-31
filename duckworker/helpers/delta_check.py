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

    cursor = connection.cursor()

    # Fetch existing table entries
    deltalake_dir = connection.execute("SELECT * FROM postgres.__deltalake_dir").fetchdf()
    existing_entries_notnull = set(row for row in deltalake_dir.loc[deltalake_dir['parent'].notnull(),"tablename"])
    existing_entries_all = set(row for row in deltalake_dir["tablename"])

    # Get directory contents
    dir_entries = set("=(^)" + entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry)))

    # Determine entries to add or remove
    entries_to_add = dir_entries - existing_entries_all
    entries_to_remove = existing_entries_notnull - dir_entries

    # Remove entries that no longer exist in the directory
    for entry in entries_to_remove:
        cursor.execute("DELETE FROM postgres.__deltalake_dir WHERE TableName = ? AND Parent IS NULL", (entry,))

    # Add new entries from the directory
    for entry in entries_to_add:
        cursor.execute("INSERT INTO postgres.__deltalake_dir (TableName, Parent, Query) VALUES (?, ?, ?)", 
                       (entry, None, None))

    connection.commit()
    
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
            # Since this is the table being created we will pull the location
            if "postgres." not in item.value:
                # If the new table isn't postgres we will assume it is local, so we will save the hostname
                location = os.getenv("HOSTNAME")
            else:
                location = "postgres"
            new_table = item.get_real_name()
            create_table_populated = True
            create_table_found = False
            
        # If the created table is found assume everything else is source
        elif create_table_populated and isinstance(item, Identifier):
            # Handle =(^)convention
            itemname = item.value
            pattern = r'\(\^\)(\w+)'
            if bool(re.search(pattern,itemname)):
                itemname = "=" + itemname
            source_tables.append(itemname)
            create_table_populated = True
    if new_table is not None:
        write_table_log(sql, new_table, source_tables, connection, location)
    return "Parsed"

def write_table_log(query, new_table, source_tables, connection, location):
    cursor = connection.cursor()
    print(new_table)
    for source_table in source_tables:
        cursor.execute("""
            INSERT INTO postgres.__deltalake_dir (TableName, Parent, Query, Loc)
            VALUES (?, ?, ?, ?)
        """, (new_table, source_table, query, location))
    

if __name__=="__main__":
    # Example usage:
    # Establish a connection to the DuckDB database
    conn = duckdb.connect(':memory:')

    # Create a cursor object using the connection
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS postgres.__deltalake_dir (
        t_id integer primary key,
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
