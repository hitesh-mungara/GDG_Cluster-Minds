FROM python:3.11-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY backend/requirements.txt backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend backend/
COPY agents agents/

# Expose port
EXPOSE 8080

# Run the application
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

# Made with Bob
