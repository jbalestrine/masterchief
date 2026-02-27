FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/masterchief

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy platform files
COPY platform/ ./platform/
COPY addons/ ./addons/
COPY docs/ ./docs/

# Create necessary directories
RUN mkdir -p /etc/masterchief /var/log/masterchief /var/lib/masterchief

# Copy default configuration
COPY config.yml /etc/masterchief/config.yml

# Expose API port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -k -f https://localhost:8443/api/health || exit 1

# Run the platform
CMD ["python3", "platform/main.py"]
