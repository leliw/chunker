#!/bin/bash

source ./docker-config.sh
EXTRA="cpu"
#EXTRA="gpu"
IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

docker run \
--gpus all \
-p 8081:8080 \
--name chunker-$EXTRA \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION