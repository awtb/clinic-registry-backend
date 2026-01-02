FROM python:3.14
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /workspace

COPY pyproject.toml .
COPY uv.lock .

RUN uv venv
RUN uv sync --frozen

COPY . .