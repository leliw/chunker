#!/bin/bash

source ./config.sh

##
# Creates a Pub/Sub topic, its associated Dead-Letter Queue (DLQ) topic,
# and three subscriptions:
# 1. A main push subscription with the DLQ configured.
# 2. A subscription for the DLQ topic for manual inspection.
# 3. A debug subscription for the main topic.
#
# Globals:
#   PROJECT_ID
#   SERVICE_ENDPOINT
#   SERVICE_ACCOUNT
# Arguments:
#   $1: The base name for the topic (e.g., "markdown-converted").
#   $2: The URL path for the push endpoint (e.g., "/pub-sub/markdown-converted").
##
create_pubsub_resources() {
    local topic_name="$1"
    local push_path="$2"
    local dlq_topic_name="${topic_name}-dlq"

    echo "Creating resources for topic: $topic_name"

    # Create the main topic
    gcloud pubsub topics create "$topic_name" --project="$PROJECT_ID" --message-retention-duration=1h

    # Create the Dead-Letter Queue (DLQ) topic
    gcloud pubsub topics create "$dlq_topic_name" --project="$PROJECT_ID" --message-retention-duration=7d

    # Create the main push subscription with DLQ configuration
    if [ -z "$push_path" ]; then
        gcloud pubsub subscriptions create "${topic_name}-sub" \
            --project="$PROJECT_ID" \
            --topic="$topic_name" \
            --ack-deadline=600 \
            --message-retention-duration=6h \
            --max-delivery-attempts=5 \
            --dead-letter-topic="$dlq_topic_name"
    else
        gcloud pubsub subscriptions create "${topic_name}-sub" \
            --project="$PROJECT_ID" \
            --topic="$topic_name" \
            --ack-deadline=600 \
            --message-retention-duration=6h \
            --max-delivery-attempts=5 \
            --dead-letter-topic="$dlq_topic_name" \
            --push-endpoint="$SERVICE_ENDPOINT$push_path" \
            --push-auth-service-account="$SERVICE_ACCOUNT"
    fi

    # Create a subscription to the DLQ topic for inspection
    gcloud pubsub subscriptions create "${dlq_topic_name}-sub" --project="$PROJECT_ID" --topic="$dlq_topic_name"

    # Create a debug subscription (pull) to the main topic
    gcloud pubsub subscriptions create "${topic_name}-debug" --project="$PROJECT_ID" --topic="$topic_name" --message-retention-duration=1h
}

create_pubsub_resources "chunking-requests"
create_pubsub_resources "chunk-embedding-requests"
