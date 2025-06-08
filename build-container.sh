#!/bin/bash

# Project directory where docker-compose.yml and .env are located
PROJECT_DIR="/volume1/docker/car-license-plate-detection"

# Service name defined in docker-compose.yml
SERVICE_NAME="car-license-plate-detection"

# Move to project directory
cd "$PROJECT_DIR" || {
  echo "[ERROR] Cannot access $PROJECT_DIR"
  exit 1
}

# Stop the service if running
if docker compose ps -q "$SERVICE_NAME" | grep -q .; then
  echo "[INFO] Stopping and removing existing container: $SERVICE_NAME"
  docker compose down
fi

# Build and start container
echo "[INFO] Building and starting service: $SERVICE_NAME"
docker compose up -d --build
