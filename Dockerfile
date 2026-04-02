# Multi-stage build for Spoorthy Quantum ERP
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r spoorthy && useradd -r -g spoorthy spoorthy

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY monitoring/ ./monitoring/
COPY pyrightconfig.json .
COPY alembic.ini .

# Create necessary directories
RUN mkdir -p /app/logs /app/exports /app/backups && \
    chown -R spoorthy:spoorthy /app

# Switch to non-root user
USER spoorthy

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/exports /app/backups && \
    chown -R spoorthy:spoorthy /app

# Switch to non-root user
USER spoorthy

# Expose port
EXPOSE 8000

# Run in development mode
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]
