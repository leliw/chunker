#!/bin/bash
INFRA_DIR=$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd)
PROJECT_ROOT=$(cd -- "$INFRA_DIR/.." &> /dev/null && pwd)

set -euo pipefail

ENVIRONMENT=${1:-dev}

REGION="europe-west3"
DOCKER_REGISTRY="${REGION}-docker.pkg.dev/development-428212/docker-eu"
IMAGE_NAME=chunker
IMAGE_TAG=$(uv run --directory="$PROJECT_ROOT" app/version.py)

# ===================== KONFIGURACJA ŚRODOWISK =====================
case $ENVIRONMENT in
  local)
    PROJECT_ID="dev-tf-497620"
    IMAGE_TAG=${2:-$(git rev-parse --short HEAD)}
    ;;
  dev)
    PROJECT_ID="dev-tf-497620"
    IMAGE_TAG=${2:-$(git rev-parse --short HEAD)}
    ;;
  prod)
    PROJECT_ID="production-456612"
    ;;
  *)
    echo "Nieznane środowisko: $ENVIRONMENT"
    exit 1
    ;;
esac

EXTRA=cpu
FULL_IMAGE_LATEST="$DOCKER_REGISTRY/$IMAGE_NAME:$EXTRA-latest"
FULL_IMAGE_TAG="$DOCKER_REGISTRY/$IMAGE_NAME:$EXTRA-$IMAGE_TAG"

echo "Sprawdzam czy obraz $FULL_IMAGE_TAG istnieje..."

# Sprawdzenie istnienia obrazu w Artifact Registry
if gcloud artifacts docker images describe $FULL_IMAGE_TAG > /dev/null 2>&1; then
    echo "✅ Obraz $FULL_IMAGE_TAG już istnieje — pomijam build."
else
    echo "❌ Obraz nie istnieje — rozpoczynam build..."
    docker build \
        --build-arg EXTRA="$EXTRA" \
        --tag $FULL_IMAGE_LATEST \
        --tag $FULL_IMAGE_TAG \
        "$PROJECT_ROOT"
    docker push $FULL_IMAGE_LATEST
    docker push $FULL_IMAGE_TAG
    echo "✅ Zbudowano i wypchnięto nowy obraz."
fi

gcloud --quiet config set project "$PROJECT_ID" 
terraform workspace select "$ENVIRONMENT" 2>/dev/null || terraform workspace new "$ENVIRONMENT"
terraform apply \
    -var="environment=${ENVIRONMENT}" \
    -var="project_id=${PROJECT_ID}" \
    -var="image_tag=${EXTRA}-${IMAGE_TAG}" \
    -var-file="${ENVIRONMENT}.tfvars"

if [ "$ENVIRONMENT" = "local" ]; then
  terraform output --raw env_vars > environments/local/.env_app
  terraform output --raw service_account_key > environments/local/.gcp_credentials.json
  docker compose -f environments/local/compose.yaml -p knowledge-base up -d
fi
