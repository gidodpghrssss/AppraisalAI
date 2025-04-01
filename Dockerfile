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
RUN mkdir -p app/templates

# Expose the port
EXPOSE 8001

# Run the application
CMD gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8001}
