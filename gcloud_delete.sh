#!/bin/bash

# This script deletes all the Google Cloud Pub/Sub resources
# created by the gcloud_create.sh script.

source ./config.sh

##
# Deletes a Pub/Sub topic, its associated Dead-Letter Queue (DLQ) topic,
# and all related subscriptions.
#
# Globals:
#   PROJECT_ID
# Arguments:
#   $1: The base name for the topic (e.g., "chunker-requests").
##
delete_pubsub_resources() {
    local topic_name="$1"
    local dlq_topic_name="${topic_name}-dlq"

    echo "Deleting resources for topic: $topic_name"

    gcloud pubsub subscriptions delete "${topic_name}-sub" --project="$PROJECT_ID" --quiet
    gcloud pubsub subscriptions delete "${topic_name}-dlq-sub" --project="$PROJECT_ID" --quiet
    gcloud pubsub subscriptions delete "${topic_name}-debug" --project="$PROJECT_ID" --quiet

    gcloud pubsub topics delete "$dlq_topic_name" --project="$PROJECT_ID" --quiet
    gcloud pubsub topics delete "$topic_name" --project="$PROJECT_ID" --quiet
}

delete_pubsub_resources "chunker-requests"
delete_pubsub_resources "chunker-embeddings-requests"