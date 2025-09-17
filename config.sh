#!/bin/bash

export SERVICE_NAME="chunker"

export REGION="europe-west3"
export PROJECT_ID="development-428212"
export PROJECT_NUMBER=$(gcloud projects list --filter="project_id=$PROJECT_ID" --format="value(project_number)")
export SERVICE_ACCOUNT="${PROJECY_NUMBER}-compute@developer.gserviceaccount.com"

export DOCKER_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/docker-eu"
export IMAGE_NAME="${SERVICE_NAME}"
export IMAGE_BASE_VERSION=$(uv run app/version.py)
