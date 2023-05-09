FROM python:3.10-slim

WORKDIR /app

RUN pip3 install --upgrade pip && \
  pip3 install wheel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV FLASK_APP=app
ENV FLASK_DEBUG=true
ENV DOCKER_DEFAULT_PLATFORM=linux/amd64
COPY . .
CMD [ "python3", "-m" , "flask", "run"]