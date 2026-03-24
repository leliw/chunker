#!/bin/bash

echo "=======> TERRAFORM <======="
cd infra
terraform init
terraform workspace select local
terraform apply --auto-approve -var-file=local.tfvars
terraform output -json | jq -r 'to_entries[] | "\(.key)=\"\(.value.value)\""' > ../.env.local
cd ..
echo "<======= TERRAFORM =======>"

# Load environment variables from .env file if it exists
# and then apply terraform output
if [ -f .env ]; then
  set -a # Automatically export all variables defined from now on
  source .env # Source the .env file
  source .env.local 
  set +a # Stop automatically exporting
fi

uv run uvicorn app.main:app --reload
