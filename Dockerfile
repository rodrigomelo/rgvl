# RGVL API - FastAPI with SQLite
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY data/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FastAPI and uvicorn
RUN pip install --no-cache-dir fastapi uvicorn pytest

# Copy application
COPY data/ .
COPY src/ .

# Create data directory
RUN mkdir -p data .backups

# Expose ports
EXPOSE 5004

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5004/api/health || exit 1

# Run API
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "5004"]
