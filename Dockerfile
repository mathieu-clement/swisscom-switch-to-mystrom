ARG APP_IMAGE=python:3.9-alpine

FROM $APP_IMAGE AS base
FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --prefix=/install -r /requirements.txt

FROM base
ENV FLASK_APP app.py
WORKDIR /project
COPY --from=builder /install /usr/local
ADD . /project

RUN apk add --no-cache curl

ENV LISTEN_HOST 127.0.0.123
ENV LISTEN_PORT 5002

ENTRYPOINT python app.py
