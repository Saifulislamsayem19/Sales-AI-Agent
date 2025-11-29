# Deployment Guide

Complete guide for deploying the Sales Analytics AI Agent to production environments.

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Server Configuration](#server-configuration)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Security Hardening](#security-hardening)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling & Performance](#scaling--performance)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (`pytest`)
- [ ] Code coverage ≥ 80%
- [ ] No critical security vulnerabilities
- [ ] Code linting passed (`flake8`, `black`)
- [ ] Type checking passed (`mypy`)

### Configuration
- [ ] Environment variables configured
- [ ] API keys secured in secrets manager
- [ ] CORS settings configured for production domain
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] Logging configured appropriately

### Security
- [ ] SSL/TLS certificates obtained
- [ ] HTTPS enforced
- [ ] API authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Security headers configured

### Performance
- [ ] Load testing completed
- [ ] Database queries optimized
- [ ] Caching strategy implemented
- [ ] Static assets compressed
- [ ] CDN configured (if applicable)

### Documentation
- [ ] API documentation updated
- [ ] Deployment runbook created
- [ ] Incident response plan documented
- [ ] Team trained on deployment process

## Deployment Options

### 1. Docker
Best for: Consistent deployments across environments

### 2. Traditional VPS
Best for: Simple, single-server deployments

### 3. Cloud Platforms
- **AWS**: Elastic Beanstalk, ECS, Lambda
- **Google Cloud**: Cloud Run, App Engine
- **Azure**: App Service, Container Instances
- **Heroku**: Simple PaaS deployment

### 4. Kubernetes
Best for: Large-scale, high-availability deployments

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL}
      - DEBUG=False
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  data:
  logs:
```

### Build and Run

```bash
# Build image
docker build -t sales-analytics-ai:latest .

# Run container
docker run -d \
  --name sales-analytics \
  -p 8000:8000 \
  --env-file .env \
  sales-analytics-ai:latest

# Or with Docker Compose
docker-compose up -d

# View logs
docker logs -f sales-analytics

# Stop container
docker stop sales-analytics

# Remove container
docker rm sales-analytics
```

## Cloud Platforms

### AWS Deployment (Elastic Beanstalk)

**1. Install EB CLI**
```bash
pip install awsebcli
```

**2. Initialize Application**
```bash
eb init -p python-3.12 sales-analytics-ai
```

**3. Create Environment**
```bash
eb create production-env
```

**4. Deploy**
```bash
eb deploy
```

**5. Configure Environment Variables**
```bash
eb setenv OPENAI_API_KEY=your-key DEBUG=False
```

### Google Cloud Run

**1. Build container**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/sales-analytics-ai
```

**2. Deploy**
```bash
gcloud run deploy sales-analytics-ai \
  --image gcr.io/PROJECT_ID/sales-analytics-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

### Heroku

**1. Create Heroku app**
```bash
heroku create sales-analytics-ai
```

**2. Add buildpack**
```bash
heroku buildpacks:set heroku/python
```

**3. Configure environment**
```bash
heroku config:set OPENAI_API_KEY=your-key
heroku config:set DEBUG=False
```

**4. Deploy**
```bash
git push heroku main
```

**5. Scale**
```bash
heroku ps:scale web=2
```

## Server Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/sales-analytics
upstream app {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/sales-analytics-access.log;
    error_log /var/log/nginx/sales-analytics-error.log;

    # Max upload size
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /app/frontend/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd Service

```ini
# /etc/systemd/system/sales-analytics.service
[Unit]
Description=Sales Analytics AI Agent
After=network.target

[Service]
Type=notify
User=appuser
Group=appuser
WorkingDirectory=/app
Environment="PATH=/app/venv/bin"
EnvironmentFile=/app/.env
ExecStart=/app/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-config /app/log_config.yaml

# Restart policy
Restart=always
RestartSec=5
StartLimitBurst=3
StartLimitInterval=60s

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/app/logs /app/data

[Install]
WantedBy=multi-user.target
```

**Manage service:**
```bash
# Enable service
sudo systemctl enable sales-analytics

# Start service
sudo systemctl start sales-analytics

# Check status
sudo systemctl status sales-analytics

# View logs
sudo journalctl -u sales-analytics -f

# Restart service
sudo systemctl restart sales-analytics
```

## Environment Setup

### Production Environment Variables

```bash
# .env.production
# ============================================
# PRODUCTION CONFIGURATION
# ============================================

# OpenAI
OPENAI_API_KEY=sk-prod-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1

# Application
DEBUG=False
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=WARNING
LOG_TO_CONSOLE=False
LOG_TO_FILE=True
LOG_FILE=/var/log/sales-analytics/app.log

# Performance
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=60

# Rate Limiting
RATE_LIMIT=100
RATE_LIMIT_WINDOW=60

# Analytics
ENABLE_ANALYTICS_CACHE=True
ANALYTICS_CACHE_TTL=7200

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=True
```

## Database Setup

### PostgreSQL (Future)

When you add database support:

```bash
# Create database
sudo -u postgres createdb sales_analytics

# Create user
sudo -u postgres createuser -P sales_user

# Grant privileges
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE sales_analytics TO sales_user;
```

### Migrations

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Security Hardening

### SSL/TLS Configuration

```bash
# Using Let's Encrypt (Certbot)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### Security Headers

Implemented in Nginx or application:

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### Secrets Management

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name sales-analytics/openai-key \
  --secret-string "your-api-key"

# Google Secret Manager
gcloud secrets create openai-api-key \
  --data-file=- <<< "your-api-key"

# HashiCorp Vault
vault kv put secret/sales-analytics openai_key=your-api-key
```

## Monitoring & Logging

### Application Monitoring

**Sentry Integration:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=settings.ENVIRONMENT
)
```

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, make_asgi_app

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### Log Aggregation

**ELK Stack:**
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Health Checks

```python
# app/api/health.py
@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.API_VERSION,
        "checks": {
            "database": await check_database(),
            "openai": await check_openai_api(),
            "disk_space": check_disk_space(),
            "memory": check_memory_usage()
        }
    }
    
    if any(not check for check in checks["checks"].values()):
        checks["status"] = "unhealthy"
        return JSONResponse(content=checks, status_code=503)
    
    return checks
```

## Scaling & Performance

### Horizontal Scaling

**Load Balancer (Nginx):**
```nginx
upstream backend {
    least_conn;
    server app1:8000 weight=1;
    server app2:8000 weight=1;
    server app3:8000 weight=1;
}
```

**Kubernetes:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sales-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sales-analytics
  template:
    metadata:
      labels:
        app: sales-analytics
    spec:
      containers:
      - name: app
        image: sales-analytics:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: sales-analytics-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: sales-analytics
```

### Caching Strategy

```python
# Redis caching
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(key: str, ttl: int = 3600):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/sales-analytics"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup data
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /app/data/

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" /app/logs/

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Upload to S3
aws s3 sync $BACKUP_DIR s3://my-bucket/backups/
```

**Cron Schedule:**
```cron
# Daily backup at 2 AM
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Disaster Recovery

1. **Regular backups** (daily automated)
2. **Off-site storage** (S3, GCS)
3. **Documented recovery procedures**
4. **Tested recovery process** (quarterly)

## Troubleshooting

### Common Issues

**Issue: High memory usage**
```bash
# Check memory
free -h

# Restart service
sudo systemctl restart sales-analytics

# Adjust worker count
# Reduce WORKERS in .env
```

**Issue: Slow responses**
```bash
# Check logs
tail -f /var/log/sales-analytics/app.log

# Monitor processes
htop

# Check database queries (if applicable)
# Enable query logging
```

**Issue: API errors**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Debugging Tools

```bash
# Application logs
docker logs sales-analytics

# System logs
journalctl -u sales-analytics -f

# Network issues
netstat -tuln | grep 8000
curl -v http://localhost:8000/health

# Performance profiling
py-spy record -o profile.svg -- python -m app.main
```

## Rollback Procedure

```bash
# Docker
docker pull sales-analytics:previous-version
docker stop sales-analytics
docker run sales-analytics:previous-version

# Git-based
git revert HEAD
git push
# Trigger deployment

# Kubernetes
kubectl rollout undo deployment/sales-analytics
kubectl rollout status deployment/sales-analytics
```

## Post-Deployment

### Smoke Tests

```bash
#!/bin/bash
# smoke-test.sh

BASE_URL="https://yourdomain.com"

# Health check
curl -f "$BASE_URL/health" || exit 1

# API test
curl -X POST "$BASE_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are my total sales?"}' || exit 1

echo "Smoke tests passed!"
```

### Monitoring Checklist

- [ ] Application responding
- [ ] Logs streaming correctly
- [ ] Metrics being collected
- [ ] Alerts configured
- [ ] SSL certificate valid
- [ ] Backups running
- [ ] Performance acceptable

---

**Need help with deployment?** Contact the team or open an issue.
