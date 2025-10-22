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

# Copy embedding models.
COPY ./data /app/data

COPY pyproject.toml uv.lock /app/

# Install application dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --extra $EXTRA

# Copy the application into the container.
COPY ./app/ /app/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

RUN python -m compileall .

# Switch to non-root user.
USER appuser

# Run the application.
EXPOSE 8080
CMD [\
    "uv", "run", "--no-dev", "--no-sync", \
    "gunicorn", "main:app", \
    "--bind", "0.0.0.0:8080", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--timeout", "300" \
    ]