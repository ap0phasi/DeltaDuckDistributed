FROM python:3.9-slim-buster

WORKDIR /usr/src/app

RUN pip install fastapi
RUN pip install uvicorn
RUN pip install websockets
RUN pip install pandas
RUN pip install deltalake
RUN pip install glob2
RUN pip install duckdb==0.9.1
RUN pip install requests
RUN pip install pyarrow
RUN pip install asyncio
RUN pip install aiormq

COPY . .

EXPOSE 8002
RUN mkdir data

# Run rpc_server.py when the container launches
CMD ["python", "delta_rpc_server.py"]