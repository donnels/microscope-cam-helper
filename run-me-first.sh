#!/bin/bash
# One-click setup script for microscope camera system
# Handles SSH setup, file copying, and runs comprehensive test

set -e

echo "=== Microscope Camera System Setup ==="
echo

# Get Pi connection details
if [ -z "$PI_USER" ]; then
    read -p "Enter Raspberry Pi username: " PI_USER
fi
if [ -z "$PI_HOST" ]; then
    read -p "Enter Raspberry Pi hostname or IP: " PI_HOST
fi
PI_IP="$PI_HOST"
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

# Check remote hardware enablement (I2C, SPI)
check_remote_interfaces() {
  ssh -o ConnectTimeout=5 "$PI_HOST" "bash -lc '
    if grep -q "dtparam=i2c_arm" /boot/config.txt /boot/firmware/config.txt /boot/firmware/usercfg.txt 2>/dev/null || [ -e /dev/i2c-1 ]; then echo I2C_ENABLED; else echo I2C_DISABLED; fi
    if grep -q "dtparam=spi" /boot/config.txt /boot/firmware/config.txt /boot/firmware/usercfg.txt 2>/dev/null || [ -e /dev/spidev0.0 ]; then echo SPI_ENABLED; else echo SPI_DISABLED; fi
  '"
}

RESULTS=$(check_remote_interfaces) || RESULTS=""
I2C_STATE=$(echo "$RESULTS" | grep I2C | tail -n1 | cut -d'_' -f2 || true)
SPI_STATE=$(echo "$RESULTS" | grep SPI | tail -n1 | cut -d'_' -f2 || true)

if [[ "$I2C_STATE" == "DISABLED" ]] || [[ "$SPI_STATE" == "DISABLED" ]]; then
  echo "Remote hardware interfaces status:"
  echo "  I2C: ${I2C_STATE:-UNKNOWN}"
  echo "  SPI: ${SPI_STATE:-UNKNOWN}"
  read -p "Enable missing interfaces (I2C/SPI) on remote and reboot now? [y/N] " ENABLE_HW
  if [[ "$ENABLE_HW" =~ ^[Yy]$ ]]; then
    echo "Enabling interfaces on remote host and rebooting..."
    ssh "$PI_HOST" "bash -lc '
      set -e
      # prefer raspi-config if available
      if command -v raspi-config >/dev/null 2>&1; then
        if [ "$I2C_STATE" = "DISABLED" ]; then sudo raspi-config nonint do_i2c 0 || true; fi
        if [ "$SPI_STATE" = "DISABLED" ]; then sudo raspi-config nonint do_spi 0 || true; fi
      else
        if [ "$I2C_STATE" = "DISABLED" ]; then sudo sed -n -e '1,200p' /boot/config.txt >/tmp/bk_config || true; sudo sed -i '/^dtparam=i2c_arm/d' /boot/config.txt || true; echo 'dtparam=i2c_arm=on' | sudo tee -a /boot/config.txt >/dev/null; fi
        if [ "$SPI_STATE" = "DISABLED" ]; then sudo sed -n -e '1,200p' /boot/config.txt >/tmp/bk_config || true; sudo sed -i '/^dtparam=spi/d' /boot/config.txt || true; echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt >/dev/null; fi
      fi
      # mark that we asked for reboot so the caller can detect
      touch ~/.microscope_reboot_requested
      sudo reboot
    '" || true

    echo "Waiting for remote host to go down for reboot..."
    sleep 5

    # Wait for host to become reachable again via SSH
    echo "Waiting for remote host to become available (will wait up to 5 minutes)..."
    MAX_WAIT=300
    INTERVAL=5
    ELAPSED=0
    while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$PI_HOST" 'echo ok' >/dev/null 2>&1; do
      sleep $INTERVAL
      ELAPSED=$((ELAPSED + INTERVAL))
      if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
        echo "Timeout waiting for host to come back. Check the device and re-run the script later."
        exit 1
      fi
    done

    echo "Remote host is back online. Resuming setup..."
  else
    echo "Proceeding without enabling hardware. You can enable I2C/SPI later and re-run the script."
  fi
fi

# Run comprehensive test (may be re-run after a reboot)
echo "Running comprehensive setup and test on Pi..."
ssh "$PI_HOST" "cd prep-scripts && ./comprehensive-test.sh"
echo

echo "=== Setup Complete ==="
echo
echo "To start the microscope service:"
echo "  ssh $PI_HOST 'cd docker && sudo docker-compose -f docker-compose.yml -f docker-compose.hardware.yml up -d'"
echo
echo "Access at: https://$PI_IP:8443"
echo
echo "To view logs:"
echo "  ssh $PI_HOST 'cd docker && sudo docker-compose -f docker-compose.yml -f docker-compose.hardware.yml logs -f'"