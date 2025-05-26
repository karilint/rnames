# ---------------------
# Stage 1: Python Build

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS python-build

# Enable bytecode compilation
# https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
# https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Disable Python downloads, because we want to
# use the system interpreter across images.
ENV UV_PYTHON_DOWNLOADS=0

# Install build dependencies
RUN apt-get update && \
    apt-get install -y build-essential default-libmysqlclient-dev pkg-config;

WORKDIR /app

# Install dependencies from uv.lock, excluding project
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project;

# Copy project files and install project + dependencies
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked;

# -----------------------
# Stage 2: Frontend Build

FROM node:24-bookworm-slim AS frontend-build

COPY ./frontend /root/frontend
WORKDIR /root/frontend
RUN npm ci && npm run build;

# --------------------
# Stage 3: Final Image

FROM python:3.13-slim-bookworm AS final-image

# Keep Python from buffering stdout and stderr
# so that they get sent to the terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies & setup user permissions
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev && \
    useradd -m user && \
    mkdir -p /vol/web/static && \
    chown -R user:user /app && \
    chown -R user:user /vol && \
    chmod -R 755 /vol/web;

USER user

# Copy virtual environment and project files
COPY --from=python-build --chown=user:user /app /app

# Copy frontend static files
COPY --from=frontend-build --chown=user:user /root/frontend/static /app/frontend/static

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

CMD ["sh", "./scripts/entrypoint.sh"]
