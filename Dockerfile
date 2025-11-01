FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir uv

RUN uv sync --no-dev

EXPOSE 8000