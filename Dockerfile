# RGVL API - Flask with SQLite
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ api/
COPY etl/ etl/
COPY data/ data/

# Create data directory if not exists
RUN mkdir -p data

# Expose API port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/api/health || exit 1

# Run API
CMD ["python", "-m", "api.main"]
