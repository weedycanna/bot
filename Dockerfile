FROM python:3.12-slim

WORKDIR /app

COPY . /app

COPY fixtures /app/fixtures

EXPOSE 8000

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .