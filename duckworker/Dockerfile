ARG worker_type

FROM python:3.9-slim-buster AS base

WORKDIR /usr/src/app

RUN pip install pandas
RUN pip install deltalake
RUN pip install glob2
RUN pip install duckdb==0.9.1
RUN pip install requests
RUN pip install pyarrow
RUN pip install asyncio
RUN pip install sqlparse

RUN mkdir data

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