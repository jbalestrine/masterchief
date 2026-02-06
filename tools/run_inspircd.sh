#!/bin/bash
# ===============================================
# Launch Inspircd container fully configured (workspace-friendly)
# ===============================================

# Set paths (adjust if you keep your config elsewhere)
# Default uses the workspace `chatops/irc/inspircd` directory if present.
HOST_IRCRC_PATH="$(pwd)/chatops/irc/inspircd"  # Change this to your ircrc/config directory
CONTAINER_NAME="inspircd"
# IMAGE can be the sha256 you provided or a tag. Using the tag is simpler locally.
IMAGE_ID="inspircd/inspircd-docker:latest"  # or use your sha256: sha256:7fc29cb14d55d2b770ccf821c975a6a8ade7227fb127eb0267b63d9e049b813f

echo "Using HOST_IRCRC_PATH=$HOST_IRCRC_PATH"

# Stop & remove existing container if exists
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Run container with config mount and exposed ports
docker run -d \
  --name $CONTAINER_NAME \
  -v "$HOST_IRCRC_PATH":/inspircd/conf \
  -p 6667:6667 \
  -p 6697:6697 \
  $IMAGE_ID

# Wait a few seconds for the server to start
sleep 5

# Show logs (stream)
docker logs -f $CONTAINER_NAME
