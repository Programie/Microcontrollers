FROM python:slim

WORKDIR /tools
COPY pyproject.toml uv.lock ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl picocom && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://github.com/astral-sh/uv/releases/download/0.7.9/uv-x86_64-unknown-linux-musl.tar.gz | tar -xz --strip-components=1 -C /usr/local/bin uv-x86_64-unknown-linux-musl/uv && \
    uv sync

ENV PATH="/tools/.venv/bin:$PATH"

WORKDIR /workdir
