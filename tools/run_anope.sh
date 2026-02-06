#!/bin/bash
# Run Anope services container and mount local config directory for customization.
# Usage: bash tools/run_anope.sh

set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ANOPE_CONF_DIR="$WORKSPACE_DIR/data/anope_conf"
CONTAINER_NAME="anope"
IMAGE="anope/anope:2.0.4" # change tag as needed

mkdir -p "$ANOPE_CONF_DIR"

echo "Anope config dir: $ANOPE_CONF_DIR"

docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

docker run -d \
  --name $CONTAINER_NAME \
  -v "$ANOPE_CONF_DIR":/anope/conf \
  --network host \
  $IMAGE || {
    echo "Failed to start Anope container. Pulling image..."
    docker pull $IMAGE
    docker run -d --name $CONTAINER_NAME -v "$ANOPE_CONF_DIR":/anope/conf --network host $IMAGE
  }

echo "Anope started (container: $CONTAINER_NAME). Check logs with: docker logs -f $CONTAINER_NAME"
