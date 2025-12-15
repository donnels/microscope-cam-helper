#!/bin/bash
# Deploy microscope container to Pi Zero
# Prerequisites: ssh-copy-id sean@10.251.2.101 (run once to set up passwordless SSH)
# Usage: ./deploy.sh

set -e

PI_HOST="sean@10.251.2.101"
REMOTE_DIR="/home/sean/microscope"

echo "Stopping services..."
ssh "$PI_HOST" "cd $REMOTE_DIR && sudo docker-compose down"

echo "Copying project to Pi..."
rsync -av --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
    ./ "$PI_HOST:$REMOTE_DIR/"

echo "Building and starting services..."
ssh "$PI_HOST" "cd $REMOTE_DIR && sudo docker-compose build && sudo docker-compose up -d"

echo "Waiting for startup..."
sleep 1

echo "Deployment complete!"
echo "Access at: https://10.251.2.101:8443/"
