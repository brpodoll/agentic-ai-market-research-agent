# Deployment Guide - AI Market Research Agent

## 🚀 Deployment Overview

This guide provides step-by-step instructions for deploying the AI Market Research Agent in various environments, from development to enterprise production.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Development](#local-development)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Platform Deployments](#cloud-platform-deployments)
6. [Enterprise On-Premise](#enterprise-on-premise)
7. [Post-Deployment](#post-deployment)

## Pre-Deployment Checklist

### Requirements Verification
- [ ] Python 3.9+ installed
- [ ] OpenAI API key obtained
- [ ] SMTP credentials configured (if using email)
- [ ] Domain/subdomain configured
- [ ] SSL certificates obtained
- [ ] Database server ready
- [ ] Redis server available
- [ ] Monitoring tools configured

### Security Checklist
- [ ] API keys stored securely
- [ ] Environment variables configured
- [ ] Firewall rules defined
- [ ] SSL/TLS enabled
- [ ] Rate limiting configured
- [ ] Backup strategy defined
- [ ] Incident response plan ready

## 🏠 Local Development

### Quick Start
```bash
# Clone repository
git clone https://github.com/your-org/market-research-agent.git
cd market-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your API keys

# Run application
python market_research_agent_enterprise.py
```

### Docker Development
```bash
# Build image
docker build -t market-research-agent:dev .

# Run container
docker run -d \
  --name mra-dev \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd):/app \
  market-research-agent:dev

# View logs
docker logs -f mra-dev
```

### Development Configuration (.env.development)
```bash
# Application
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=DEBUG

# API Keys
OPENAI_API_KEY=sk-dev-...
ANTHROPIC_API_KEY=sk-ant-dev-...

# Database
DATABASE_URL=sqlite:///dev.db

# Cache
REDIS_URL=redis://localhost:6379/0

# Email (Optional)
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=dev_user
SMTP_PASSWORD=dev_pass
```

## 🎭 Staging Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
```bash
# Instance specifications
- Type: t3.large (2 vCPU, 8 GB RAM)
- OS: Ubuntu 22.04 LTS
- Storage: 50 GB SSD
- Security Group: Allow 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

#### 2. Initial Server Setup
```bash
# Connect to server
ssh -i your-key.pem ubuntu@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3-pip nginx certbot python3-certbot-nginx redis-server postgresql

# Install Node.js (for PM2)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2
```

#### 3. Application Setup
```bash
# Create app directory
sudo mkdir -p /opt/market-research-agent
sudo chown ubuntu:ubuntu /opt/market-research-agent

# Clone repository
cd /opt/market-research-agent
git clone https://github.com/your-org/market-research-agent.git .

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.staging .env
nano .env  # Add your staging credentials
```

#### 4. Database Setup
```bash
# Setup PostgreSQL
sudo -u postgres psql

CREATE DATABASE mra_staging;
CREATE USER mra_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE mra_staging TO mra_user;
\q

# Run migrations (if applicable)
python manage.py migrate
```

#### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/market-research-agent
server {
    listen 80;
    server_name staging.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/market-research-agent/static;
        expires 30d;
    }

    client_max_body_size 100M;
}
```

#### 6. SSL Setup
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/market-research-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install SSL certificate
sudo certbot --nginx -d staging.yourdomain.com
```

#### 7. Process Management with PM2
```bash
# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'mra-staging',
    script: 'python',
    args: 'app.py',
    cwd: '/opt/market-research-agent',
    interpreter: '/opt/market-research-agent/venv/bin/python',
    env: {
      NODE_ENV: 'staging'
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Docker Compose Staging
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  app:
    build: .
    environment:
      - APP_ENV=staging
      - DATABASE_URL=postgresql://mra:password@db:5432/mra_staging
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=mra_staging
      - POSTGRES_USER=mra
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

## 🌟 Production Deployment

### High-Availability Architecture

```
                    ┌─────────────┐
                    │   Route53   │
                    │     DNS     │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   CloudFront│
                    │     CDN     │
                    └──────┬──────┘
                           │
                  ┌────────┴────────┐
                  │   Application   │
                  │  Load Balancer  │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴─────┐    ┌─────┴─────┐   ┌─────┴─────┐
    │   App     │    │   App     │   │   App     │
    │  Server 1 │    │  Server 2 │   │  Server 3 │
    └─────┬─────┘    └─────┬─────┘   └─────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
            ┌─────┴─────┐    ┌─────┴─────┐
            │PostgreSQL │    │   Redis   │
            │  Primary  │    │  Cluster  │
            └─────┬─────┘    └───────────┘
                  │
            ┌─────┴─────┐
            │PostgreSQL │
            │  Replica  │
            └───────────┘
```

### Kubernetes Production Deployment

#### 1. Namespace and Secrets
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: market-research-prod

---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mra-secrets
  namespace: market-research-prod
type: Opaque
stringData:
  openai-api-key: "sk-prod-..."
  database-url: "postgresql://user:pass@db-host:5432/mra_prod"
  redis-url: "redis://redis-host:6379/0"
  smtp-password: "smtp-password-here"
```

#### 2. ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mra-config
  namespace: market-research-prod
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  SMTP_HOST: "smtp.sendgrid.net"
  SMTP_PORT: "587"
  MAX_WORKERS: "4"
```

#### 3. Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mra-deployment
  namespace: market-research-prod
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: market-research-agent
  template:
    metadata:
      labels:
        app: market-research-agent
    spec:
      containers:
      - name: app
        image: your-registry/market-research-agent:v1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: mra-config
        - secretRef:
            name: mra-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 4. Service and Ingress
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mra-service
  namespace: market-research-prod
spec:
  selector:
    app: market-research-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mra-ingress
  namespace: market-research-prod
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: mra-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mra-service
            port:
              number: 80
```

#### 5. Horizontal Pod Autoscaler
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mra-hpa
  namespace: market-research-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mra-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## ☁️ Cloud Platform Deployments

### AWS Deployment

#### Using Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.10 market-research-agent

# Create environment
eb create production --instance-type t3.large

# Deploy
eb deploy

# Set environment variables
eb setenv OPENAI_API_KEY=$OPENAI_API_KEY DATABASE_URL=$DATABASE_URL

# Enable HTTPS
eb config
# Edit and add SSL certificate configuration
```

#### Using ECS Fargate
```json
// task-definition.json
{
  "family": "market-research-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-ecr-repo/market-research-agent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/market-research-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Azure Deployment

#### Using App Service
```bash
# Create resource group
az group create --name mra-prod --location eastus

# Create App Service plan
az appservice plan create \
  --name mra-plan \
  --resource-group mra-prod \
  --sku P1V2 \
  --is-linux

# Create web app
az webapp create \
  --resource-group mra-prod \
  --plan mra-plan \
  --name market-research-agent \
  --runtime "PYTHON:3.10"

# Configure app settings
az webapp config appsettings set \
  --resource-group mra-prod \
  --name market-research-agent \
  --settings OPENAI_API_KEY=$OPENAI_API_KEY

# Deploy code
az webapp deployment source config \
  --name market-research-agent \
  --resource-group mra-prod \
  --repo-url https://github.com/your-org/market-research-agent \
  --branch main \
  --manual-integration
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/market-research-agent

# Deploy to Cloud Run
gcloud run deploy market-research-agent \
  --image gcr.io/PROJECT-ID/market-research-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="APP_ENV=production" \
  --set-secrets="OPENAI_API_KEY=openai-key:latest" \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=1 \
  --max-instances=10
```

## 🏢 Enterprise On-Premise Deployment

### Prerequisites
- RHEL 8+ or Ubuntu 20.04+ servers
- Docker Enterprise or Kubernetes cluster
- Enterprise proxy configuration
- Active Directory/LDAP integration

### Installation Script
```bash
#!/bin/bash
# enterprise-install.sh

set -e

# Configuration
INSTALL_DIR="/opt/market-research-agent"
SERVICE_USER="mra-service"
LOG_DIR="/var/log/market-research-agent"

# Create service user
sudo useradd -r -s /bin/false $SERVICE_USER

# Create directories
sudo mkdir -p $INSTALL_DIR $LOG_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR $LOG_DIR

# Install dependencies
sudo yum install -y python39 python39-pip nginx redis postgresql-server

# Setup PostgreSQL
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb mra_production
sudo -u postgres createuser mra_user

# Install application
cd $INSTALL_DIR
sudo -u $SERVICE_USER git clone https://github.com/your-org/market-research-agent.git .
sudo -u $SERVICE_USER python3.9 -m venv venv
sudo -u $SERVICE_USER ./venv/bin/pip install -r requirements.txt

# Configure systemd service
cat > /etc/systemd/system/market-research-agent.service << EOF
[Unit]
Description=Market Research Agent
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable market-research-agent
sudo systemctl start market-research-agent

echo "Installation complete!"
```

### High Availability Setup
```bash
# HAProxy configuration for load balancing
# /etc/haproxy/haproxy.cfg

global
    maxconn 4096
    log 127.0.0.1 local0

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend web_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/mra.pem
    redirect scheme https if !{ ssl_fc }
    default_backend web_servers

backend web_servers
    balance roundrobin
    option httpchk GET /health
    server web1 192.168.1.10:8000 check
    server web2 192.168.1.11:8000 check
    server web3 192.168.1.12:8000 check
```

## 📮 Post-Deployment

### Verification Checklist
- [ ] Application accessible via HTTPS
- [ ] Health check endpoint responding
- [ ] Database connections working
- [ ] Redis cache operational
- [ ] Email sending functional
- [ ] API authentication working
- [ ] Rate limiting active
- [ ] Monitoring alerts configured
- [ ] Backup jobs scheduled
- [ ] Log rotation configured

### Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'market-research-agent'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Market Research Agent",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Analysis Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, analysis_duration_seconds)"
          }
        ]
      }
    ]
  }
}
```

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://api.yourdomain.com/health

# Stress testing with Locust
locust -f locustfile.py --host=https://api.yourdomain.com
```

### Security Scanning
```bash
# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.yourdomain.com

# Dependency vulnerability check
pip install safety
safety check

# SSL/TLS check
nmap --script ssl-enum-ciphers -p 443 api.yourdomain.com
```

### Backup Verification
```bash
# Test database backup
pg_dump -h localhost -U mra_user -d mra_production > backup.sql

# Test restore
createdb mra_test
psql -h localhost -U mra_user -d mra_test < backup.sql

# Verify backup integrity
pg_dump mra_test | md5sum
```

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
tail -f /var/log/market-research-agent/app.log

# Verify environment variables
env | grep OPENAI

# Test database connection
psql -h localhost -U mra_user -d mra_production -c "SELECT 1"

# Check port availability
netstat -tulpn | grep 8000
```

#### High Memory Usage
```bash
# Check memory usage
ps aux | grep python

# Analyze memory leaks
py-spy dump --pid <PID>

# Restart workers
pm2 restart all
```

#### Slow Response Times
```bash
# Check database performance
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Analyze slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# Check Redis performance
redis-cli INFO stats
```

### Rollback Procedure
```bash
# Kubernetes rollback
kubectl rollout undo deployment/mra-deployment -n market-research-prod

# Docker rollback
docker stop mra-prod
docker run -d --name mra-prod your-registry/market-research-agent:previous-version

# Database rollback
psql -h localhost -U mra_user -d mra_production < backup-previous.sql
```

## 📚 Additional Resources

- [API Documentation](/docs/api.md)
- [Monitoring Guide](/docs/monitoring.md)
- [Security Best Practices](/docs/security.md)
- [Disaster Recovery Plan](/docs/disaster-recovery.md)

---

*For emergency support, contact the DevOps team via PagerDuty or call the on-call engineer.*