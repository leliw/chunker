# ------ Stage 1: Load models ------
    FROM python:3.12-slim AS models

    # The installer requires curl (and certificates) to download the release archive
    RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
   
    # Creates a non-root user with an explicit UID and adds permission to access the /app folder
    RUN mkdir /app
    RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

    # Download the latest installer
    ADD https://astral.sh/uv/install.sh /uv-installer.sh

    # Run the installer then remove it
    RUN sh /uv-installer.sh && rm /uv-installer.sh

    # Ensure the installed binary is on the `PATH`
    ENV PATH="/root/.local/bin/:$PATH"
    # Copy uv for non-root user
    RUN cp /root/.local/bin/uv /usr/local/bin/uv

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
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-dev

    COPY pyproject.toml uv.lock /app/

    # Install the project's **extra** dependencies using the lockfile and settings
    RUN --mount=type=cache,target=/root/.cache/uv \
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-dev --extra CPU

    # Load the embedding model.
    RUN echo '__version__ = ""' > /app/version.py
    COPY ./load_models.py ./app/config.py /app/
    RUN uv run --no-dev load_models.py && rm /app/load_models.py
# ------ Stage 2: Python/FastAPI project ------
    FROM python:3.12-slim

    ARG EXTRA="cpu"
    ARG MODEL_NAME="ipipan/silver-retriever-base-v1.1"

    # The installer requires curl (and certificates) to download the release archive
    RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

    # Creates a non-root user with an explicit UID and adds permission to access the /app folder
    RUN mkdir /app
    RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

    # Download the latest installer
    ADD https://astral.sh/uv/install.sh /uv-installer.sh

    # Run the installer then remove it
    RUN sh /uv-installer.sh && rm /uv-installer.sh

    # Ensure the installed binary is on the `PATH`
    ENV PATH="/root/.local/bin/:$PATH"
    # Copy uv for non-root user
    RUN cp /root/.local/bin/uv /usr/local/bin/uv

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
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-dev

    COPY pyproject.toml uv.lock /app/

    # Install the project's **extra** dependencies using the lockfile and settings
    RUN --mount=type=cache,target=/root/.cache/uv \
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-dev --extra $EXTRA

    # Copy embedding models.
    COPY --from=models /app/data /app/data
    
    # Copy the application into the container.
    COPY ./app/ /app/
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv sync --locked --no-dev --extra $EXTRA

    # Place executables in the environment at the front of the path
    ENV PATH="/app/.venv/bin:$PATH"

    # Run the application.
    EXPOSE 8080
    CMD ["uv", "run", "--no-dev", "gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "main:app"]