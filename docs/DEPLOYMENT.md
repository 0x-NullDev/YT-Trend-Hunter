# Deployment Guide

## Overview

YT Trend Hunter can be deployed in multiple ways:

- **Docker Compose** (recommended for VPS)
- **Railway** (easiest)
- **Render** (good balance)
- **AWS** (most scalable)

---

## Prerequisites

- Docker & Docker Compose
- YouTube Data API v3 key
- AI provider API key (DeepSeek, OpenAI, or Anthropic)
- Domain name (optional)
- SSL certificate (optional, for production)

---

## 1. Docker Compose Deployment (VPS)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/yt-trend-hunter.git
cd yt-trend-hunter
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your production values
```

### Step 3: Start Services

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Step 5: Create Admin User

```bash
docker-compose exec backend python -m app.scripts.create_admin
```

### Step 6: Setup SSL (Optional)

```bash
# Using Let's Encrypt with Nginx
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

---

## 2. Railway Deployment

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Initialize Project

```bash
railway init
railway link
```

### Step 3: Add Services

```bash
# Add PostgreSQL
railway add postgres

# Add Redis
railway add redis
```

### Step 4: Configure Environment Variables

```bash
railway variables set YOUTUBE_API_KEY=your_key
railway variables set AI_API_KEY=your_key
railway variables set AI_PROVIDER=openai
railway variables set SECRET_KEY=your_secret
```

### Step 5: Deploy

```bash
railway up
```

---

## 3. Render Deployment

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | yt-trend-hunter-backend |
| **Environment** | Docker |
| **Branch** | main |
| **Plan** | Starter or higher |

### Step 2: Add Environment Variables

Add these in the Render dashboard:

```
YOUTUBE_API_KEY=your_key
AI_API_KEY=your_key
AI_PROVIDER=openai
SECRET_KEY=your_secret
DATABASE_URL=from_render_postgres
REDIS_URL=from_render_redis
```

### Step 3: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Copy the Internal Connection String
3. Add it as `DATABASE_URL` in your Web Service

### Step 4: Create Redis Instance

1. Click "New +" → "Redis"
2. Copy the Connection String
3. Add it as `REDIS_URL` in your Web Service

### Step 5: Deploy Frontend

Create another Web Service for the frontend:

| Setting | Value |
|---------|-------|
| **Name** | yt-trend-hunter-frontend |
| **Environment** | Node |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |
| **Root Directory** | frontend |

Environment variables:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 4. AWS Deployment

### Option A: ECS with Fargate

```bash
# Build images
docker build -t yt-trend-hunter-backend ./backend
docker build -t yt-trend-hunter-frontend ./frontend

# Push to ECR
aws ecr create-repository --repository-name yt-trend-hunter-backend
aws ecr create-repository --repository-name yt-trend-hunter-frontend

docker push your-account.dkr.ecr.region.amazonaws.com/yt-trend-hunter-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/yt-trend-hunter-frontend:latest

# Create ECS cluster and services
# Use the task-definitions in deploy/aws/
```

### Option B: EC2 with Docker Compose

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-instance

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/yourusername/yt-trend-hunter.git
cd yt-trend-hunter
cp .env.example .env
# Edit .env
docker-compose up -d
```

---

## 5. Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `YOUTUBE_API_KEY` | ✅ | YouTube Data API v3 key | - |
| `AI_PROVIDER` | ✅ | AI provider (deepseek/openai/anthropic/ollama) | openai |
| `AI_API_KEY` | ✅* | AI provider API key | - |
| `AI_MODEL` | ❌ | AI model name | gpt-4 |
| `AI_BASE_URL` | ❌ | AI base URL (for Ollama) | - |
| `DATABASE_URL` | ✅ | PostgreSQL connection string | postgresql+asyncpg://postgres:postgres@db:5432/yt_trend_hunter |
| `REDIS_URL` | ✅ | Redis connection string | redis://redis:6379/0 |
| `ELASTICSEARCH_URL` | ❌ | Elasticsearch URL | http://elasticsearch:9200 |
| `SECRET_KEY` | ✅ | JWT secret key | - |
| `ENVIRONMENT` | ❌ | Environment (development/production) | development |
| `LOG_LEVEL` | ❌ | Logging level | INFO |
| `CORS_ORIGINS` | ❌ | Allowed CORS origins | http://localhost:3000 |

*Not required for Ollama (local)

---

## 6. Scaling

### Vertical Scaling
- Increase VPS resources (CPU, RAM)
- Upgrade PostgreSQL plan
- Upgrade Redis plan

### Horizontal Scaling
- Add more backend instances behind a load balancer
- Use Redis Cluster for distributed caching
- Use PostgreSQL read replicas
- Add Elasticsearch for search scaling

### Performance Optimization
- Enable Redis caching for API responses
- Use Celery for async task processing
- Implement pagination for all list endpoints
- Use database indexing
- Enable query optimization

---

## 7. Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Redis health
docker-compose exec redis redis-cli ping

# Database health
docker-compose exec db pg_isready
```

### Logging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# View recent errors
docker-compose logs --tail=100 backend | grep ERROR
```

### Backup
```bash
# Backup database
docker-compose exec db pg_dump -U postgres yt_trend_hunter > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres yt_trend_hunter
```

---

## 8. Troubleshooting

### Common Issues

**Issue**: API returns 503 Service Unavailable
**Solution**: Check if database and Redis are running

```bash
docker-compose ps
docker-compose logs db
docker-compose logs redis
```

**Issue**: YouTube API quota exceeded
**Solution**: Add multiple API keys or upgrade YouTube API quota

**Issue**: Celery tasks not executing
**Solution**: Check Redis connection and Celery worker logs

```bash
docker-compose logs celery-worker
docker-compose exec redis redis-cli ping
```

**Issue**: Database connection refused
**Solution**: Wait for database to be ready, check connection string

```bash
docker-compose logs db
docker-compose exec db pg_isready
```

---

## 9. Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Monitor API usage
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Never commit .env file
