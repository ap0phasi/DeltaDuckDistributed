CREATE TABLE IF NOT EXISTS __deltalake_dir (
    t_id SERIAL, 
    TableName VARCHAR,
    Parent VARCHAR,
    Query VARCHAR,
    Loc VARCHAR
);

CREATE TABLE IF NOT EXISTS __worker_list (
    t_id SERIAL, 
    worker_id VARCHAR
);