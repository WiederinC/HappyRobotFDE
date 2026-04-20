FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY api/requirements.txt ./api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy project source
COPY api/ ./api/
COPY dashboard/ ./dashboard/

# Data directory for SQLite
RUN mkdir -p /data

# Seed on startup then serve
ENV DATABASE_URL=sqlite:////data/carrier.db

EXPOSE 8000

# Seed the DB then start the server
# Use $PORT if set (Railway), otherwise default to 8000
CMD ["sh", "-c", "python -m api.seed && uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
