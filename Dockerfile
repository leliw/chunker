FROM python:3.13.9-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG EXTRA="cpu"

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN mkdir /app
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev --extra $EXTRA

# Copy embedding models.
COPY ./data /app/data

COPY pyproject.toml uv.lock /app/

# Copy the application into the container.
COPY ./app/ /app/


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user.
USER appuser

# Run the application.
EXPOSE 8080
CMD ["sh", "-c", "uv run --no-dev gunicorn --bind 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker --workers ${WORKERS:-1} --timeout 300 main:app"]
