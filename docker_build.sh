#!/bin/bash

source ./config.sh

set -euo pipefail

# uv run load_models.py

for EXTRA in "cpu" "gpu"
do
    echo "Building for $EXTRA..."
    EXTRA="$EXTRA"
    IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

    docker build \
    --build-arg EXTRA="$EXTRA" \
    --tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION .
    # --progress=plain \
    echo "Pushing $EXTRA..."
    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION
done