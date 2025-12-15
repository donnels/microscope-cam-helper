#!/bin/bash
set -e

# Get video device from environment (use VIDEO_DEVICE consistently)
VIDEO_DEVICE="${VIDEO_DEVICE:-/dev/video0}"

# Wait for USB device to be available
echo "Waiting for video device: $VIDEO_DEVICE"
timeout=30
counter=0

while [ ! -e "$VIDEO_DEVICE" ] && [ $counter -lt $timeout ]; do
    sleep 1
    counter=$((counter + 1))
done

if [ ! -e "$VIDEO_DEVICE" ]; then
    echo "ERROR: $VIDEO_DEVICE not found after ${timeout}s"
    echo "Available video devices:"
    ls -la /dev/video* 2>/dev/null || echo "No video devices found"
    exit 1
fi

# Display device information
echo "Found video device:"
v4l2-ctl --device="$VIDEO_DEVICE" --all

# Get supported formats
echo "Supported formats:"
v4l2-ctl --device="$VIDEO_DEVICE" --list-formats-ext

echo "Starting microscope web interface..."
echo "  Device: $VIDEO_DEVICE"
echo "  Resolution: ${VIDEO_WIDTH:-1280}x${VIDEO_HEIGHT:-720}"
echo "  FPS: ${VIDEO_FPS:-30}"
echo "  Port: ${WEB_PORT:-8080}"
echo "  HTTPS: ${ENABLE_HTTPS:-true}"

# Start Flask web interface
cd /app
exec python3 web_server.py
