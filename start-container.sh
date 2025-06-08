#!/bin/bash

# Load environment variables from .env file
set -a
. .env
set +a

# Container name to monitor
CONTAINER_NAME="car-license-plate-detection"
IMAGE_NAME="chrispolewiak/plate-detector:latest"

# Pull the latest image from DockerHub
echo "[INFO] Pulling latest image from DockerHub: $IMAGE_NAME"
docker pull $IMAGE_NAME

# Stop and remove old container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[INFO] Removing existing container: ${CONTAINER_NAME}"
  docker stop "$CONTAINER_NAME" >/dev/null 2>&1
  docker rm "$CONTAINER_NAME" >/dev/null 2>&1
fi

# Ensure necessary directories exist
mkdir -p "$DETECTED_PATH" "$LOGS_PATH"

# Run the container using pulled image
echo "[INFO] Starting container: ${CONTAINER_NAME}"
docker run -d \
  --name "$CONTAINER_NAME" \
  -e TZ="$TZ" \
  -v "$DETECTED_PATH":/app/detected \
  -v "$LOGS_PATH":/app/logs \
  -v "$WATCHLIST_PATH":/app/plates_watchlist.json:ro \
  "$IMAGE_NAME"