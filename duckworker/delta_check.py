import os
import duckdb
import re

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
    
def log_query(query, connection):
    cursor = connection.cursor()
    
    # This regex will match simple CREATE TABLE queries and capture the new table name and the source table name.
    create_table_pattern = re.compile(r"CREATE TABLE IF NOT EXISTS (\w+)\s+AS\s+SELECT \* FROM (\w+)", re.IGNORECASE)
    match = create_table_pattern.search(query)
    
    create_table_pattern_alt = re.compile(r"CREATE TABLE IF NOT EXISTS (\w+)\s+AS\s+SELECT \* FROM =\(\^\)(\w+)", re.IGNORECASE)
    match_alt = create_table_pattern_alt.search(query)
    
    if match:
        new_table, source_table = match.groups()
        cursor.execute("""
            INSERT INTO __deltalake_dir (TableName, Parent, Query)
            VALUES (?, ?, ?)
        """, (new_table, source_table, query))
    elif match_alt:
        new_table, source_table = match_alt.groups()
        cursor.execute("""
            INSERT INTO __deltalake_dir (TableName, Parent, Query)
            VALUES (?, ?, ?)
        """, (new_table, "=(^)" + source_table, query))
    else:
        # For handling joins, you might want to look for JOIN clauses and extract table names.
        # This would be a simplified example and may not work for all queries.
        join_pattern = re.compile(r"JOIN (\w+)", re.IGNORECASE)
        tables_involved = join_pattern.findall(query)
        if tables_involved:
            # You would need to define how you want to handle multiple tables in the Parent column.
            # This example just converts the list to a string.
            parents = ', '.join(tables_involved)
            # Assuming the new table is created as a result of SELECT INTO statement.
            # This is a simplified approach and would need to be adjusted for your specific use case.
            new_table_pattern = re.compile(r"INTO (\w+)", re.IGNORECASE)
            new_table_match = new_table_pattern.search(query)
            if new_table_match:
                new_table = new_table_match.group(1)
                cursor.execute("""
                    INSERT INTO __deltalake_dir (TableName, Parent, Query)
                    VALUES (?, ?, ?)
                """, (new_table, parents, query))

    # Commit the changes
    connection.commit()

if __name__=="__main__":
    # Example usage:
    # Establish a connection to the DuckDB database
    conn = duckdb.connect(':memory:')

    # Call the function with the path to the directory and the connection
    log_tables('data/deltalake', conn)

    # Don't forget to close the connection when you're done
    conn.close()
