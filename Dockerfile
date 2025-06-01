FROM python:alpine

WORKDIR /tools
COPY pyproject.toml uv.lock ./
RUN apk add curl && \
    curl -sSL https://github.com/astral-sh/uv/releases/download/0.7.9/uv-x86_64-unknown-linux-musl.tar.gz | tar -xz --strip-components=1 -C /usr/local/bin uv-x86_64-unknown-linux-musl/uv && \
    uv sync

ENV PATH="/tools/.venv/bin:$PATH"

WORKDIR /workdir
