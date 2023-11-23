ARG worker_type

FROM python:3.9-slim-buster AS base

WORKDIR /usr/src/app

RUN pip install pandas
RUN pip install deltalake
RUN pip install glob2
RUN pip install duckdb --pre --upgrade
RUN pip install requests
RUN pip install pyarrow
RUN pip install asyncio
RUN pip install sqlparse

RUN mkdir data

# # Postgres Installations
# # Install build dependencies (e.g., git, build-essential for compiling C++ code)
# RUN apt-get update && apt-get install -y \
#     make \
#     cmake \ 
#     git \
#     build-essential \
#     libssl-dev \
#     libpq-dev \
#     g++ \
#     ninja-build \
#     curl \ 
#     && rm -rf /var/lib/apt/lists/*

# # Clone the postgres_scanner extension repository
# RUN git clone https://github.com/duckdb/postgres_scanner.git postgres_scanner

# # Clone DuckDB into the expected subdirectory
# RUN git clone https://github.com/duckdb/duckdb.git postgres_scanner/duckdb

# WORKDIR /usr/src/app/postgres_scanner   
# RUN GEN=ninja make

# If the worker_version is api
FROM base AS branch-version-api
# Unique package installation
RUN pip install fastapi
RUN pip install uvicorn
COPY helpers/ .
COPY api/ .
EXPOSE 8003
CMD ["uvicorn", "duckworker:app", "--reload", "--host", "0.0.0.0", "--port", "8003"]

# If the worker_version is rpc
FROM base AS branch-version-rpc
# Unique package installation
RUN pip install aiormq
COPY helpers/ .
COPY rpc/ .
# Run rpc_server.py when the container launches
CMD ["python", "duck_rpc_server.py"]

FROM branch-version-${worker_type} AS final