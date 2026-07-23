# ==========================================
# STAGE 1: Builder (Installs dependencies)
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system build tools needed for compiling dependencies (e.g., C extensions for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels into a standalone directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==========================================
# STAGE 2: Production Runtime (Clean & Lean)
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install ONLY runtime shared libraries (libpq for Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create a non-root user for container security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Copy application source code
COPY --chown=appuser:appuser . .

# Expose app port and run with uvicorn
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]