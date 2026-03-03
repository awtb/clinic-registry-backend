FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    gcc \
    libpq-dev \
    iputils-ping \
    cloc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/clinic-registry-backend
