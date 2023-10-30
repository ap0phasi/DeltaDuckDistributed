FROM python:3.9-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN pip install fastapi
RUN pip install uvicorn
RUN pip install websockets
RUN pip install requests
RUN pip install asyncio
RUN pip install numpy
RUN pip install pandas

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]