FROM python:3.12-slim

ARG EXTRA="cpu"
ARG MODEL_NAME="ipipan/silver-retriever-base-v1.1"

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev --extra $EXTRA

COPY pyproject.toml uv.lock /app/

# Load the embedding model.
COPY ./load_model.py ./app/config.py /app/
ENV MODEL_NAME=$MODEL_NAME
RUN uv run load_model.py && rm /app/load_model.py

# Copy the application into the container.
COPY ./app/ /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --extra $EXTRA

# Run the application.
EXPOSE 8080
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "main:app"]