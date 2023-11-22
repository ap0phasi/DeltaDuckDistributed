CREATE TABLE IF NOT EXISTS __deltalake_dir (
    t_id INTEGER PRIMARY KEY, 
    TableName VARCHAR,
    Parent VARCHAR,
    Query VARCHAR
)