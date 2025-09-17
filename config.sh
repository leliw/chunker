#!/bin/bash

export MODEL_NAME="ipipan/silver-retriever-base-v1.1"
export DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
export IMAGE_NAME="chunker"
export IMAGE_BASE_VERSION=$(uv run app/version.py)
