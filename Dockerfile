FROM python:3.13.1-slim

WORKDIR /app

COPY requirements ./requirements
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY static ./static
COPY src ./src
COPY tests ./tests
COPY .env .
