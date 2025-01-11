# Stage 1: Base build stage
FROM python:3.12-slim AS builder
 
WORKDIR /app
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim

# Create user and required directories with proper permissions
RUN useradd -m -r appuser && \
    mkdir -p /app/staticfiles /app/static && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

# Copy application code and set permissions
COPY --chown=appuser:appuser . .
RUN chmod -R 755 /app/staticfiles

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["gunicorn", "jobless.wsgi:application", "--bind", "0.0.0.0:8000"]