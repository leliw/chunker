#!/bin/bash

source ./config.sh
source ./docker_build.sh

EXTRA="cpu"
IMAGE_VERSION="$EXTRA-$IMAGE_BASE_VERSION"

sed -e "s/{{SERVICE_NAME}}/$SERVICE_NAME/g" \
    -e "s/{{PROJECT_ID}}/$PROJECT_ID/g" \
    -e "s/{{REGION}}/$REGION/g" \
    -e "s#{{DOCKER_REGISTRY}}#$DOCKER_REGISTRY#g" \
    -e "s/{{IMAGE_NAME}}/$IMAGE_NAME/g" \
    -e "s/{{IMAGE_VERSION}}/$IMAGE_VERSION/g" \
    gcp-service.template.yaml > gcp-service.yaml
gcloud run services replace gcp-service.yaml --region $REGION
rm gcp-service.yaml

gcloud run services proxy $SERVICE_NAME --region $REGION
``