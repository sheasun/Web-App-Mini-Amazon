# FROM python:3.8.13-alpine3.15
FROM python:3
ENV PYTHONUNBUFFERED 1

ADD . /app

WORKDIR /app

RUN chmod +x run_server.sh
# RUN apk add build-base
RUN pip install -r requirements.txt
