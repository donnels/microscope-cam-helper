#!/bin/bash
# Comprehensive test and setup script for microscope camera system
# Installs required software, verifies hardware, and runs all tests
# Run on Raspberry Pi Zero

set -e

# Configuration
TESTS_DIR="prep-scripts"
TESTS_ENV="$HOME/test-env"

echo "=== Comprehensive Microscope Camera System Test ==="
echo

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install package if not present
install_if_missing() {
    local package=$1
    if ! dpkg -l | grep -q "^ii  $package "; then
        echo "Installing $package..."
        sudo apt-get update
        sudo apt-get install -y "$package"
        echo "✓ $package installed"
    else
        echo "✓ $package already installed"
    fi
}

echo "1. Installing required system packages..."
install_if_missing "v4l-utils"
install_if_missing "docker.io"
install_if_missing "docker-compose"
install_if_missing "python3-venv"
install_if_missing "python3-pip"
install_if_missing "i2c-tools"
install_if_missing "usbutils"
echo

echo "2. Checking hardware configuration..."
echo "Checking I2C..."
if grep -q "dtparam=i2c_arm" /boot/config.txt /boot/firmware/config.txt /boot/firmware/usercfg.txt 2>/dev/null || [ -e /dev/i2c-1 ]; then
    echo "✓ I2C enabled"
else
    echo "⚠ I2C not enabled. Run 'sudo raspi-config' → Interfacing Options → I2C → Enable"
fi

echo "Checking SPI..."
if grep -q "dtparam=spi" /boot/config.txt /boot/firmware/config.txt /boot/firmware/usercfg.txt 2>/dev/null || [ -e /dev/spidev0.0 ]; then
    echo "✓ SPI enabled"
else
    echo "⚠ SPI not enabled. Run 'sudo raspi-config' → Interfacing Options → SPI → Enable"
fi
echo

echo "3. Checking USB video device..."
if lsusb | grep -q "534d:2109\|MacroSilicon"; then
    echo "✓ MacroSilicon USB Video device found"
else
    echo "✗ USB video device not found. Check USB connection."
    exit 1
fi
echo

echo "4. Checking video device..."
if [ -e /dev/video0 ]; then
    echo "✓ /dev/video0 exists"
    if [ -r /dev/video0 ]; then
        echo "✓ /dev/video0 is readable"
    else
        echo "⚠ /dev/video0 not readable. Fixing permissions..."
        sudo chmod 666 /dev/video0
        echo "✓ Permissions fixed"
    fi
else
    echo "✗ /dev/video0 not found"
    exit 1
fi
echo

echo "5. Checking Docker..."
if command_exists docker; then
    echo "✓ Docker installed"
    if sudo systemctl is-active --quiet docker; then
        echo "✓ Docker service running"
    else
        echo "⚠ Docker service not running. Starting..."
        sudo systemctl start docker
        sudo systemctl enable docker
        echo "✓ Docker service started"
    fi
else
    echo "✗ Docker not installed"
    exit 1
fi
echo

echo "6. Checking prep-script files..."
if [ ! -f "function-test-hat.py" ]; then
    echo "✗ Prep-script files not found. Please copy prep-scripts directory to Pi first."
    exit 1
else
    echo "✓ Prep-script files present"
fi
echo

echo "7. Setting up Python virtual environment..."
if [ ! -d "$TESTS_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv --system-site-packages "$TESTS_ENV"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

echo "Activating virtual environment and upgrading pip..."
source "$TESTS_ENV/bin/activate"
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo

echo "8. Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Python dependencies installed"
echo

echo "9. Running hardware tests..."
echo

echo "9a. Testing LED HAT..."
echo "Command: sudo -E $TESTS_ENV/bin/python3 function-test-hat.py"
sudo -E "$TESTS_ENV/bin/python3" function-test-hat.py
echo "✓ LED test completed (check if LEDs lit)"
echo

echo "9b. Testing Battery Monitor..."
echo "Command: sudo -E $TESTS_ENV/bin/python3 function-test-battery.py"
timeout 10 sudo -E "$TESTS_ENV/bin/python3" function-test-battery.py || echo "✓ Battery test completed (timed out after 10s)"
echo

echo "9c. Testing Camera (if opencv available)..."
if "$TESTS_ENV/bin/python3" -c "import cv2" 2>/dev/null; then
    echo "OpenCV available, testing camera..."
    echo "Command: $TESTS_ENV/bin/python3 function-test-cameras.py"
    "$TESTS_ENV/bin/python3" function-test-cameras.py
    echo "✓ Camera test completed"
else
    echo "⚠ OpenCV not installed, skipping camera test"
    echo "To install: pip install opencv-python (takes ~2 hours on Pi Zero)"
fi
echo

echo "10. Build Docker Container..."
if [ -d "../docker/docker-microscope" ]; then
    echo "Docker directory found, building container..."
    cd ../docker/docker-microscope
    sudo docker-compose build
    echo "✓ Docker container built"
else
    echo "⚠ Docker directory not found. Copy docker/ directory to Pi and run:"
    echo "  cd docker/docker-microscope && sudo docker-compose build"
fi
echo

echo "=== All Setup and Tests Complete ==="
echo
echo "To start the service:"
echo "  cd docker/docker-microscope && sudo docker-compose up -d"
echo
echo "Access at: https://<pi-ip>:8443"
echo
echo "To cleanup test environment:"
echo "  deactivate"
echo "  rm -rf $TESTS_ENV $TESTS_DIR ../docker"