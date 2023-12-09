# Sord: a Pocket-Sized Data Fabric using distributed DuckDB workers

> **sord**  
> */sɔːd/*  
> _noun_
> 1. A flock of mallard ducks.


A lightweight, distributed platform for data analysis demonstrating integration of Vue 3 with Vite and Vuetify for the frontend, a robust Python WebSocket backend, and advanced data handling using DeltaTables, Postgres, and DuckDB. This project aims to provide seamless real-time data querying with distributed DeltaLake and DuckDB workers, all separately containerized with Docker for scalability and responsiveness. 

## Overview

This project is structured into four main components:

* **Vue 3 Frontend** Developed using Vue 3 along with Vite for fast development and Vuetify for a material design interface.
* **Python Websocket Backend** A Python WebSocket server for real-time communication, using FastAPI as the connecting gateway to our data workers.
* **DeltaLake+DuckDB Data Management** Persistent storage is managed via DeltaTables, with DuckDB serving as the querying engine and temporary storage mechanism.
* **Containerized Data Workers** Separate containers are used for DeltaLake and DuckDB workers, communicating with the backend via FastAPI. 

## Installation

Clone the repository to your local machine:

```
git clone https://github.com/ap0phasi/DeltaDuckDistributed.git
```

## Usage

Build and run the Docker containers:
```
docker-compose up --build
```

You can access the vue frontend at **http://localhost:80**.

### DeltaLake Management
The worker containers share a volume mount to the data folder in the parent directory. The DeltaLake worker is configured to parse all the csvs in a provided raw data directory and create a DeltaTable. So if we have some csv files in the directory *data/raw/climate* we can use the dashboard to load the data into a DeltaLake on the **DeltaLake Manage** tab:

![DeltaLake Load](https://github.com/ap0phasi/DeltaDuckDistributed/blob/main/media/DeltaLake_Load1.png)

As the DeltaLake worker expects the subdirectory containing the csv files to be in *data/raw*, we can just provide the subdirectory name. We can choose if we want to create/overwrite a DeltaTable or if we want to append to an existing one. Finally, we provide the name of the DeltaTable and then press Load. After a moment we will see our DeltaLake directory table indicates the DeltaTable was successfully loaded. 

### DuckDB Analysis
Once DeltaTables are created, our DuckDB worker can be used to directly query this DeltaTable in a zero-copy streaming fashion to produce charts and tables. As queries can be used to also create in-memory DuckDB tables, we will need a way to specify if we are trying to read from a DeltaTable or a DuckDB table. To accomplish this we introduce a new query convention to specify the reading from a DeltaTable:
```
SELECT * FROM =(^)myclimate
```
The **=(^)** decorator used before a table name tells the DuckDB worker to query from a DeltaTable of that name. 

Users can select if they want the query response to be a *Message*, *Chart*, or *Table*. Instead of rendering the entire query result in a chart or table, users can specify with the slider how many data points they want rendered. This does not impact the querying itself; the entire query is performed by the worker container in a zero-copy streaming fashion, with just the user-specified slice converted into the JSONs required for rendering charts and tables. 

![DuckDB Query](https://github.com/ap0phasi/DeltaDuckDistributed/blob/main/media/DuckDB_Query.png)

As previously mentioned, queries can be used to make an in-memory DuckDB table:

```
CREATE TABLE IF NOT EXISTS temptable1 AS (SELECT * FROM =(^)myclimate)
```

This DuckDB table can then be queried without the **=(^)** decorator.

```
SELECT * FROM temptable1
```

### Additional Features

#### DuckDB Query Tracking

A feature unique to this tool is the ability to track the queries used to create in-memory DuckDB tables in a zero-copy streaming fashion. On the DeltaLake Management page, loaded DeltaTables are displayed with the =(^) convention. If you run a query such as:

```
CREATE TABLE IF NOT EXISTS temp1 AS SELECT * FROM =(^)climate
```
The *temp1* table will be created in-memory and the DeltaLake Management page will update showing the new table, the query used to create it, and the parent tables from which the new table is derived. This also works for **JOIN** and **UNION** queries such as:

```
CREATE TABLE IF NOT EXISTS temp2 AS SELECT * FROM =(^)climate UNION ALL SELECT * FROM temp1
```
In a case like this where a DeltaTable is being unioned with an in-memory DuckDB table, a new row entry in our DeltaLake tracker will be added for each parent table:

![DeltaLake Tracking](https://github.com/ap0phasi/DeltaDuckDistributed/blob/main/media/DeltaLake_Tracker.png)

#### Custom DuckDB Connections

In **Settings** a custom DuckDB connection string can be provided, allowing for users to provide tokens for MotherDuck connections. 

#### Responsiveness Tests
To see the responsiveness of the WebSocket + FastAPI combination, use the following query:

```
=(^)quack
```

This generates a random dataframe to display. 


#### DuckDB functionality

For tables within the DuckDB database, familiar DuckDB functionality such as ```DESCRIBE SELECT * FROM mytable``` and ```SHOW TABLES``` work within this dashboard. 


## Full Distribution with RabbitMQ RPCs + Postgres Scanner

The functionality shown accomplishes distribution in separatation of DeltaLake management processes from DuckDB query processes, but what if we want to further distribute with multiple Delta and Duck Workers? 

### Messaging to Workers

We can easily spin up multiple workers using Docker's ```replicate``` functionality, but how do we send messages to these workers in a reliable fashion? We could maintain a number of FastAPI connections and cycle requests round-robin, but that wouldn't allow for workers picking up tasks based on their availability. Instead, RabbitMQ is used for message queuing, with the workers updated to a RPC client-server system. This keeps application reactivity by allowing workers to take on long-running tasks while other workers handle other requests.

Note that with this update, either *api* or *rpc* workers can be used, as configured in the **.env** file.

### Temporary Data Persistence Across Distributed Workers

With the distribution of workers, we have the new issue of how to make sure any temporary data generated by processes like ```CREATE TABLE``` are available for all workers. As DuckDB defaults to an in-memory connection, if we created a DuckDB table, that table would only exist on the worker that handled that request. While DuckDB can persist data locally to a db file, we cannot have multiple write connections to that file, and even if we were to have multiple files, a read-only mount of a DuckDB file to one worker prohibits it from being used for writing by another worker. 

The "true" persistent storage for this framework is intended to be the DeltaLake, so temporary data could be written as DeltaTables, but for cleanliness it is appropriate to offer some temporary storage capability. 

Therefore, Postgres is utilized for temporary storage to create persistence across workers. At the time of this writing, the official DuckDB Postgres Scanner extension is intended only for reading from Postgres, however an improvement is under development that offers read and write functionality, so this build utilizes the Bleeding Edge GitHub version of DuckDB. Data can be saved to Postgres with the following query pattern:

```
CREATE TABLE IF NOT EXISTS postgres.temptable AS SELECT * FROM =(^)climate
```

Note all Postgres data must have the "postgres" schema, otherwise temporary tables will default to saving in DuckDB. 

The management of Postgres just for temporary data persistence between workers adds some overhead, especially considering in the current release a worker needs to detach and reattach to Postgres to ensure they have the most up-to-date data. This added computational cost is managed by pre-filtering queries and only refreshing the Postgres connection if "postgres" appears in the query. 

If there is no need to run a distributed swarm of workers, it is recommended that API workers are used and temporary data is stored simply on that worker's DuckDB instance to reduce complexity. 

### Writing Temporary Data to DeltaLake

With the persistence of temporary data using Postgres, there is the added benefit of being able to share data between our separate Duck and Delta workers, meaning Delta workers can now write DeltaTables from temporary Postgres tables. The CSV ingestion used by the Delta worker is simply DuckDB's sniffer function ran as a SELECT * query, so functionality was added to the Delta worker to accept either a file path or a full DuckDB query. This allows for a Delta Table to be created by entering a query like this into the *CSV Folder Path* field:

```
SELECT * FROM postgres.temptable
```

## DuckDB Parallelization within a Single WebSocket Connection

The use of distributed Duck and Delta workers is primarily focused around maintaining responsiveness for multiple connections to the websocket. However, this distribution can be leveraged for parallelization of requests on a single websocket connection. This project utilizes a custom query pipeline format where queries can be allocated to different Duck workers and executed in parallel based on their dependence on one another. As an example, a query pipeline can take the following form:

```
-- id: 1
CREATE TABLE postgres.temp1 AS SELECT * FROM =(^)climate;

-- id: 2
CREATE TABLE postgres.temp2 AS SELECT * FROM =(^)climate;

-- id: 3
-- depends_on: 1,2
SELECT * FROM postgres.temp1
UNION ALL
SELECT * FROM postgres.temp2;
```

Where ```depends_on``` refers to the ```id``` provided in each query decorator. If no ```depends_on``` is provided, it is assumed there is no dependence. The websocket backend constructs a dependency graph based on these decorators to create query packets. In this case, as queries 1 and 2 are not dependent on any other queries, they are bundled together into a single packet, where each query in the packet is sent to different DuckDB workers to be executed in parallel. Query 3, being dependent on 1 and 2, is only executed after the parallel execution of 1 and 2 finishes. 

This offers flexibility and structure to the default behavior of websockets, where within a connection, subsequent requests are not submitted to the message queue until previous responses are received. By explicitly stating what operations can happen in parallel versus sequentially, users can maximize the utilization of DuckDB workers. 

## Node Specification for In-Memory Utilization

The functionality showcased above allows for multiple DuckDB workers to share data across a number of persistent data sources. However, there are scenarios where we want to save temporary data but do not need it accessible to other DuckDB workers. Doing so allows us to utilize the DuckDB's significantly higher speed when accessing data stored in RAM. As DuckDB workers default to in-memory, we can simply save a table like this:

```
CREATE TABLE eph1 AS SELECT * FROM =(^)climate
```

However, if we have multiple DuckDB workers running, when we submit this request it will be added to our RabbitMQ and an available worker will pick up the request. Subsequent requests are not guarenteed to be picked up by the same worker, so queries like:

```
SELECT * FROM eph1
```

Are expected to fail in most cases save for the lucky scenario where the same Duck worker that picked up the original request to create the table picks up this subsequent query. To avoid this inconvenience, functionality has been added for DuckDB worker listing, table tracking, and worker specification. 

### DuckDB Worker Tracking

Rendering this query as a table

```
SELECT * FROM postgres.__worker_list
```

Will show the worker ids of all DuckDB workers. 

### Table Tracking

Table tracking now includes the location of the data on the DeltaLake Management page. If the data is in the persistent shared postgres it will be labeled as such, data in the DeltaLake will be not have a Location value, and data stored in-memory on the workers will be labeled with the respective worker id. 

### Worker Specification

Users can now specify what worker they want an operation to be performed by using the following convention:

```
-- id: 1
-- node: <worker_id>
<query>;
```
Don't forget the semi-colon! To follow along with the previous example, if our DeltaLake Management page indicates ```eph``` is stored on *cb391c323181*, we can run this query: 

```
-- id: 1
-- node: cb391c323181
SELECT * FROM eph1;
```
We will find this query is always successful, because performing the above specification routes the RPC request to a dedicated message queue just for the specified worker instead of the general queue to be picked up by any available worker. 

The ability to specify nodes within the RabbitMQ + RPC coordination system allows users to temporarily store highly accessible data on a single node for extremely fast DuckDB operations, but the real power can be demonstrated in operations like this:

```
-- id: 1
-- node: cb391c323181
CREATE TABLE eph2 AS SELECT * FROM eph1;

-- id: 2
CREATE TABLE postgres.para1 AS SELECT * FROM =(^)climate;

-- id: 3
-- depends_on: 1,2
-- node: cb391c323181
CREATE TABLE eph3 AS
SELECT * FROM eph2
UNION ALL
SELECT * FROM postgres.para1;
```

Here, based on the dependency graph, query 1 and 2 will run simultaneously, where query 1 saves *eph2* in-memory and query 2 writes a table to the shared Postgres storage. Query 3 depends on both of these tables to save a unioned table in-memory, so it waits until the simultaneous executions of queries 1 and 2 finish before running. And of course, whenever you want to persist data off of RAM, you can always run:

```
-- id: 1
-- node: cb391c323181
CREATE TABLE postgres.eph1 AS SELECT * FROM eph1;
```

## MotherDuck Functionality

As this application also works for MotherDuck connections, MotherDuck can be used for data persistence instead of a local Postgres. 


## Demo

Please see the short demo below:
![DeltaDuck Demo](https://github.com/ap0phasi/DeltaDuckDistributed/blob/main/media/DeltaDuck_Demo.gif)
