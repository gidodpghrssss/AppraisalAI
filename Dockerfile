FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p app/data/files app/data/embeddings app/static/css app/static/js app/static/images

# Expose the port
EXPOSE 8002

# Run the application
CMD ["python", "run.py", "--api-only"]
