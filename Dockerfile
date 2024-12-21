FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt /bot/
RUN pip install -r /bot/requirements.txt
COPY . /bot/

CMD python3 /botn/app.py