# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip3 install --upgrade pip && \
  pip3 install wheel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV FLASK_APP=app
ENV APP_CONFIG_FILE=config/development.py
ENV FLASK_DEBUG=true
COPY . .

CMD [ "python3", "-m" , "flask", "run"]