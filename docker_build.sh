#!/bin/bash

source ./docker_config.sh

for EXTRA in "cpu" "gpu"
do
    echo "Building for $EXTRA..."
    EXTRA="$EXTRA"
    IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

    docker build \
    --build-arg EXTRA="$EXTRA" \
    --build-arg MODEL_NAME="$MODEL_NAME" \
    --tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION .
    # --progress=plain \

done

for EXTRA in "cpu" "gpu"
do
    echo "Pushing $EXTRA..."
    IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION
done