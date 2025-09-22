#!/usr/bin/env bash
# Simple helper to rebuild the Docker image and optionally restart docker-compose
# Usage:
#   ./scripts/update_image.sh            # build image only
#   ./scripts/update_image.sh --compose  # build image then docker-compose up -d

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="bpi-collector:latest"

cd "$ROOT_DIR"

echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

if [ "${1-}" = "--compose" ]; then
  echo "Bringing up docker-compose services (detached)..."
  docker-compose up -d --build
fi

echo "Done."
