# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Python and necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv wget && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and install the dependencies
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the entrypoint to use the virtual environment's Python
ENTRYPOINT ["/app/venv/bin/python", "main.py"]