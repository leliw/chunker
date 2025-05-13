#!/bin/bash

EXTRA="cpu"
#EXTRA="gpu"
MODEL_NAME="ipipan/silver-retriever-base-v1"
DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME="chunker"
IMAGE_VERSION="$EXTRA-0.0.2"


docker build \
--build-arg EXTRA="$EXTRA" \
--build-arg MODEL_NAME="$MODEL_NAME" \
# --progress=plain \
--tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION .

docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION