# Distributed DeltaLake+DuckDB Dashboard

A lightweight, distributed platform for data analysis demonstrating integration of Vue 3 with Vite and Vuetify for the frontend, a robust Python WebSocket backend, and advanced data handling using DeltaTables and DuckDB. This project aims to provide seamless real-time data querying with distributed DeltaLake and DuckDB workers, all separately containerized with Docker for scalability and responsiveness. 

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

![DeltaLake Load](https://github.com/ap0phasi/DeltaDuckDistributed/blob/main/media/DeltaLake_Load.png)

As the DeltaLake worker expects the subdirectory containing the csv files to be in *data/raw*, we can just provide the subdirectory name. We can choose if we want to create/overwrite a DeltaTable or if we want to append to an existing one. Finally, we provide the name of the DeltaTable and then press Load. After a moment the message should indicate the DeltaTable was successfully created or updated. 

### DuckDB Analysis
Once DeltaTables are created, our DuckDB worker can be used to directly query this DeltaTable in a zero-copy streaming fashion to produce charts and tables. As queries can be used to also create in-memory DuckDB tables, we will need a way to specify if we are trying to read from a DeltaTable or a DuckDB table. To accomplish this we introduce a new query convention to specify the reading from a DeltaTable:
```
SELECT * FROM =(^)myclimate
```
The **=(^)** decorator used before a table name tells the DuckDB worker to query from a DeltaTable of that name. 

Users can select if they want the query response to be a *Message*, *Chart*, or *Table*. Instead of rendering the entire query result in a chart or table, users can specify with the slider how many data points they want rendered. This does impact the querying itself; the entire query is performed by the worker container in a zero-copy streaming fashion, with just the user-specified slice converted into the JSONs required for rendering charts and tables. 

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

#### Custom DuckDB Connections

In **Settings** a custom DuckDB connection string can be provided, allowing for users to provide tokens for MotherDuck connections. 

#### Responsiveness Tests
To see the responsiveness of the WebSocket + FastAPI combination, use the following query:

```
=(^)quack
```

This generates a random dataframe to display. 