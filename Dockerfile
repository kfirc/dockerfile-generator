FROM python:3.11-slim

# Install system dependencies including Docker
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directory for build contexts
RUN mkdir -p build_context

# Set environment variable for the bind mount directory
ENV MOUNT_PATH=/mnt/host

# Create mount point for host files
RUN mkdir -p /mnt/host

# Set entrypoint to run main.py
ENTRYPOINT ["python", "main.py"]
