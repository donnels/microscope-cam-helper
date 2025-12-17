#!/bin/bash
set -e

echo "Starting CSI Camera Service..."

# Wait for devices to be available
echo "Waiting for CSI camera devices..."
while [ ! -e /dev/video0 ]; do
    echo "Waiting for /dev/video0..."
    sleep 1
done

echo "CSI camera devices ready."

# Start the web server
exec python3 web_server.py