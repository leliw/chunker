#!/bin/bash

EXTRA="cpu"
#EXTRA="gpu"
DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME="chunker"
IMAGE_VERSION="$EXTRA-0.0.5"

docker run \
--gpus all \
-p 8081:8080 \
--name chunker-$EXTRA \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION