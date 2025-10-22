#!/bin/bash

export PROJECT_ID="development-428212"
# export PROJECT_ID="production-456612"
export REGION="europe-west3"
export DOCKER_REGISTRY="${REGION}-docker.pkg.dev/development-428212/docker-eu"
# export DOCKER_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/docker-eu"

export SERVICE_NAME="chunker"

export PROJECT_NUMBER=$(gcloud projects list --filter="project_id=$PROJECT_ID" --format="value(project_number)")
export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

export SERVICE_ENDPOINT="https://${SERVICE_NAME}-${PROJECT_NUMBER}.${REGION}.run.app"

export IMAGE_NAME="${SERVICE_NAME}"
export IMAGE_BASE_VERSION=$(uv run --no-sync app/version.py)
