#!/bin/bash

MODEL_NAME="ipipan/silver-retriever-base-v1.1"
DOCKER_REGISTRY="europe-west3-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME="chunker"
# Base image version, EXTRA will be prepended
IMAGE_BASE_VERSION="0.0.4"

for EXTRA in "cpu" "gpu"
do
    echo "Building for $EXTRA..."
    IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

    docker build \
    --build-arg EXTRA="$EXTRA" \
    --build-arg MODEL_NAME="$MODEL_NAME" \
    --tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION .
    # --progress=plain \

    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION
done