# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Install system dependencies for audio and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    gcc \
    python3-dev \
    git \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Create a volume for memory persistence
VOLUME /app/memory

# Run easy-jarvis
CMD ["python3", "src/main.py"]
