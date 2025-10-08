FROM python:3.11-slim
LABEL maintainer="Thomas <thomas.s.liu@gmail.com>"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=4
ENV GUNICORN_PORT=5000
ENV RDS_MYSQL_HOST=$RDS_MYSQL_HOST
ENV RDS_MYSQL_PORT=$RDS_MYSQL_PORT
ENV RDS_MYSQL_USER=$RDS_MYSQL_USER
ENV RDS_MYSQL_PASS=$RDS_MYSQL_PASS
ENV RDS_MYSQL_DB=$RDS_MYSQL_DB
ENV REDIS_HOST=$REDIS_HOST
ENV REDIS_PORT=$REDIS_PORT
ENV REDIS_DB=$REDIS_DB
ENV REDIS_PASSWORD=$REDIS_PASSWORD

# Create non-root user
RUN useradd -m appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app && chmod -R 755 /app

# Switch to non-root user
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:${GUNICORN_PORT}/health || exit 1

# Run with gunicorn
CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS} -b 0.0.0.0:${GUNICORN_PORT} emissions_api:create_app"]