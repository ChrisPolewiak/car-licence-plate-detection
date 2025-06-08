#!/bin/bash

# Load environment variables from .env file
set -a
. .env
set +a

# Container name to monitor
CONTAINER_NAME="car-license-plate-detection"

# Check if the container is already running
if docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "[INFO] Container already running. Skipping launch."
    exit 0
fi

# If stopped container exists, remove it
if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "[INFO] Removing old stopped container..."
    docker rm $CONTAINER_NAME
fi


# Start the container (auto-remove after exit)
docker run -d \
  --name $CONTAINER_NAME \
  -e SOURCE_DIR=$SOURCE_DIR \
  -e TARGET_DIR=$TARGET_DIR \
  -e TARGET_TEST_DIR=$TARGET_TEST_DIR \
  -e LOGS_DIR=$LOGS_DIR \
  -e TZ=$TZ \
  -v $IMPORT_PATH:$SOURCE_DIR \
  -v $LIBRARY_PATH:$TARGET_DIR \
  -v $LIBRARYTEST_PATH:$TARGET_TEST_DIR \
  -v $LOGS_PATH:$LOGS_DIR \
  -u ${LINUX_UID}:${LINUX_GID} \
  car-license-plate-detection

