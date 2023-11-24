CREATE TABLE IF NOT EXISTS __deltalake_dir (
    t_id SERIAL, 
    TableName VARCHAR,
    Parent VARCHAR,
    Query VARCHAR
)