FROM python:3.12-slim

ARG EXTRA="cpu"
ARG MODEL_NAME="ipipan/silver-retriever-base-v1.1"

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
# Install the application dependencies.
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --extra $EXTRA --no-cache

# Load the embedding model.
COPY ./load_model.py ./app/config.py /app/
ENV MODEL_NAME=$MODEL_NAME
RUN uv run load_model.py && rm /app/load_model.py

# Copy the application into the container.
COPY ./app/ /app/

# Run the application.
EXPOSE 8080
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "main:app"]