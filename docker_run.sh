#!/bin/bash

EXTRA="cpu"
#EXTRA="gpu"
DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME="chunker"
IMAGE_BASE_VERSION=$(uv run app/config.py)
IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

docker run \
--gpus all \
-p 8081:8080 \
--name chunker-$EXTRA \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION