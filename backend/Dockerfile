FROM python:3.9-slim-buster

WORKDIR /usr/src/app

RUN pip install fastapi
RUN pip install uvicorn
RUN pip install websockets
RUN pip install requests
RUN pip install asyncio
RUN pip install numpy
RUN pip install pandas
RUN pip install aiormq
RUN pip install aiohttp

COPY . .

# Define the build-time argument
ARG delta_worker_type
ARG duck_worker_type

# Set the runtime environment variable from the build-time argument
ENV delta_worker_type=${delta_worker_type}
ENV duck_worker_type=${duck_worker_type}

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]