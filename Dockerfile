FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ecommerce_api.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p logs staticfiles media && \
    chmod -R 777 logs staticfiles media

# Create and switch to non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Copy project files
# This is done last to ensure that changes to the code don't invalidate the cache for the requirements
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run the application
CMD ["gunicorn", "ecommerce_api.wsgi:application", "--bind", "0.0.0.0:8000"]
