# Use Python base image
FROM python:3.10-slim

# Set environment variable for transformers cache
ENV TRANSFORMERS_CACHE=/tmp/hf_cache

# Create app directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Expose the port
EXPOSE 7860

# Run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
