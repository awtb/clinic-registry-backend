FROM python:3.14

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    iputils-ping \
    black \
    cloc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
