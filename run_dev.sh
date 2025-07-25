#!/bin/bash

# Load environment variables from .env file if it exists
# This allows for easy configuration of the development environment
if [ -f .env ]; then
  set -a # Automatically export all variables defined from now on
  source .env # Source the .env file
  set +a # Stop automatically exporting
fi

.venv/bin/python -m uvicorn app.main:app --reload