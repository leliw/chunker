#!/bin/bash

source ./config.sh
# EXTRA="cpu"
EXTRA="gpu"
IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

docker run \
--rm \
--env LOG_LOG_CONFIG=DEBUG \
--env LOG_FEATURES__EMBEDDINGS__EMBEDDING_SERVICE=DEBUG \
--gpus all \
-p 8081:8080 \
--name chunker-$EXTRA \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION
