#!/bin/bash
# One-click setup script for microscope camera system
# Handles SSH setup, file copying, and runs comprehensive test

set -e

echo "=== Microscope Camera System Setup ==="
echo

# Get Pi connection details
read -p "Enter Raspberry Pi username: " PI_USER
read -p "Enter Raspberry Pi hostname or IP: " PI_HOST
PI_HOST="$PI_USER@$PI_HOST"
echo

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "No SSH key found. Generating one..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "✓ SSH key generated"
else
    echo "✓ SSH key exists"
fi
echo

# Setup SSH access
echo "Setting up SSH access to $PI_HOST..."

# First, add host key to known_hosts
ssh-keyscan -H "$PI_HOST" >> ~/.ssh/known_hosts 2>/dev/null || true

# Test SSH with key
if ! ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=5 "$PI_HOST" "echo 'SSH test'" 2>/dev/null; then
    echo "SSH key authentication failed. Attempting to copy key..."
    if ssh-copy-id -o StrictHostKeyChecking=no "$PI_HOST" 2>/dev/null; then
        echo "✓ SSH access configured"
    else
        echo "⚠ ssh-copy-id failed. Please run manually:"
        echo "  ssh-copy-id $PI_HOST"
        echo "Then re-run this script."
        exit 1
    fi
else
    echo "✓ SSH access already configured"
fi
echo

# Copy directories
echo "Copying prep-scripts and docker directories to Pi..."
scp -r prep-scripts docker "$PI_HOST:~/"
echo "✓ Directories copied"
echo

# Run comprehensive test
echo "Running comprehensive setup and test on Pi..."
ssh "$PI_HOST" "cd prep-scripts && ./comprehensive-test.sh"
echo

echo "=== Setup Complete ==="
echo
echo "To start the microscope service:"
echo "  ssh $PI_HOST 'cd docker/docker-microscope && sudo docker-compose up -d'"
echo
echo "Access at: https://$PI_HOST:8443"
echo
echo "To view logs:"
echo "  ssh $PI_HOST 'cd docker/docker-microscope && sudo docker-compose logs -f'"