#!/bin/bash

#EXTRA="cpu"
EXTRA="gpu"
MODEL_NAME="ipipan/silver-retriever-base-v1.1"
DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME="chunker"
IMAGE_VERSION="$EXTRA-0.0.3"


docker build \
--build-arg EXTRA="$EXTRA" \
--build-arg MODEL_NAME="$MODEL_NAME" \
--tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION .
# --progress=plain \

docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION