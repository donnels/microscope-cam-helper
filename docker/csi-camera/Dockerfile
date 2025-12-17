# Use Raspberry Pi optimized base image for ARMv6 support
FROM balenalib/raspberry-pi-debian:bullseye

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal dependencies for CSI camera, web interface
# Note: libcamera-tools provides libcamera-vid and libcamera-still commands
RUN apt-get update && \
    apt-get install -y \
    bash \
    libcamera-tools \
    libcamera0 \
    python3 \
    python3-pip \
    python3-flask \
    python3-numpy \
    openssl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Generate self-signed SSL certificate
RUN mkdir -p /app/certs && \
    openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout /app/certs/key.pem \
    -out /app/certs/cert.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=VSaGCR/CN=csi-camera.local"

# Expose web interface ports (HTTP and HTTPS)
EXPOSE 8081 8444

# Copy application files
COPY camera_service.py /app/
COPY web_server.py /app/
COPY docker_entrypoint.sh /app/
RUN chmod +x /app/docker_entrypoint.sh

ENTRYPOINT ["/app/docker_entrypoint.sh"]