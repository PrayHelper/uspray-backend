FROM python:3.10-slim

WORKDIR /app

RUN pip3 install --upgrade pip && \
  pip3 install wheel

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run"]
