# Use Raspberry Pi optimized base image for ARMv6 support
FROM balenalib/raspberry-pi-debian:bullseye

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal dependencies for video capture, web interface, and Unicorn HAT
RUN apt-get update && \
    apt-get install -y \
    v4l-utils \
    python3 \
    python3-pip \
    python3-opencv \
    python3-flask \
    python3-spidev \
    python3-rpi.gpio \
    python3-numpy \
    python3-smbus \
    i2c-tools \
    libatlas-base-dev \
    openssl \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Pimoroni Unicorn HAT and I2C libraries
RUN pip3 install --no-cache-dir unicornhat smbus2

# Create working directory
WORKDIR /app

# Generate self-signed SSL certificate
RUN mkdir -p /app/certs && \
    openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout /app/certs/key.pem \
    -out /app/certs/cert.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=VSaGCR/CN=microscope.local"

# Expose web interface ports (HTTP and HTTPS)
EXPOSE 8080 8443

# Copy application files
COPY camera_service.py /app/
COPY web_server.py /app/
COPY docker_entrypoint.sh /app/
RUN chmod +x /app/docker_entrypoint.sh

ENTRYPOINT ["/app/docker_entrypoint.sh"]
