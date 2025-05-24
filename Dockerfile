FROM python

WORKDIR /tools
COPY pyproject.toml uv.lock ./
RUN curl -sSL https://github.com/astral-sh/uv/releases/download/0.7.8/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xz --strip-components=1 -C /usr/local/bin uv-x86_64-unknown-linux-gnu/uv && \
    uv sync

ENV PATH="/tools/.venv/bin:$PATH"

WORKDIR /workdir
