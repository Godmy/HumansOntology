# HumansOntology Deployment Guide

This guide explains how to deploy HumansOntology in different environments.

## Table of Contents

1. [Environment Overview](#environment-overview)
2. [Development Environment](#development-environment)
3. [Production Environment](#production-environment)
4. [Quick Start Commands](#quick-start-commands)
5. [Troubleshooting](#troubleshooting)

## Environment Overview

The project supports two main environments:

- **Development (`dev`)**: For local development with hot reload and debugging tools
- **Production (`prod`)**: For production deployment with optimizations and security

## Development Environment

### Prerequisites

- Docker Desktop installed
- Git installed
- At least 4GB RAM available

### Setup

1. **Copy environment file:**
   ```bash
   cp .env.dev .env
   ```

2. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Access services:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - GraphQL Playground: http://localhost:8000/graphql
   - MailPit Web UI: http://localhost:8025 (email testing)
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

### Development Features

- **Hot Reload**: Both frontend and backend automatically reload on code changes
- **MailPit**: All emails are captured and viewable at http://localhost:8025
- **Debug Mode**: Detailed error messages and logging
- **Seed Data**: Database is automatically seeded with test data
- **Volume Mounts**: Source code is mounted for instant updates

### Stopping Development Environment

```bash
# Stop containers
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (clean slate)
docker-compose -f docker-compose.dev.yml down -v
```

## Production Environment

### Prerequisites

- Docker and Docker Compose installed on server
- Domain name configured
- SSL certificates (recommended)
- At least 8GB RAM available

### Setup

1. **Create production environment file:**
   ```bash
   cp .env.prod.example .env.prod
   ```

2. **Generate secure secrets:**
   ```bash
   # Generate JWT secret
   openssl rand -hex 32

   # Generate database password
   openssl rand -base64 32

   # Generate Redis password
   openssl rand -base64 32
   ```

3. **Edit `.env.prod` with your values:**
   ```env
   # Database
   DB_PASSWORD=<generated-password>

   # Redis
   REDIS_PASSWORD=<generated-password>

   # JWT
   JWT_SECRET_KEY=<generated-secret>

   # Domain
   ALLOWED_ORIGINS=https://yourdomain.com
   FRONTEND_URL=https://yourdomain.com
   VITE_GRAPHQL_ENDPOINT=https://yourdomain.com/graphql

   # Email (example with SendGrid)
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=<your-sendgrid-api-key>
   FROM_EMAIL=noreply@yourdomain.com

   # OAuth (optional)
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>

   # Monitoring (optional but recommended)
   SENTRY_DSN=<your-sentry-dsn>
   SENTRY_ENABLE_TRACING=true
   ```

4. **Configure Nginx (if using reverse proxy):**

   Create `nginx/nginx.conf`:
   ```nginx
   events {
       worker_connections 1024;
   }

   http {
       upstream backend {
           server backend:8000;
       }

       upstream frontend {
           server frontend:3000;
       }

       server {
           listen 80;
           server_name yourdomain.com;

           # Redirect HTTP to HTTPS
           return 301 https://$server_name$request_uri;
       }

       server {
           listen 443 ssl http2;
           server_name yourdomain.com;

           ssl_certificate /etc/nginx/ssl/cert.pem;
           ssl_certificate_key /etc/nginx/ssl/key.pem;

           # Security headers
           add_header X-Frame-Options "SAMEORIGIN" always;
           add_header X-Content-Type-Options "nosniff" always;
           add_header X-XSS-Protection "1; mode=block" always;

           # Backend API
           location /graphql {
               proxy_pass http://backend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

           location /api {
               proxy_pass http://backend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

           location /docs {
               proxy_pass http://backend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
           }

           location /health {
               proxy_pass http://backend;
               proxy_set_header Host $host;
           }

           # Frontend
           location / {
               proxy_pass http://frontend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;

               # WebSocket support for HMR (not needed in production, but good to have)
               proxy_http_version 1.1;
               proxy_set_header Upgrade $http_upgrade;
               proxy_set_header Connection "upgrade";
           }
       }
   }
   ```

5. **Deploy:**
   ```bash
   # Load production environment
   export $(cat .env.prod | xargs)

   # Build and start
   docker-compose -f docker-compose.prod.yml up --build -d

   # Check logs
   docker-compose -f docker-compose.prod.yml logs -f
   ```

6. **Verify deployment:**
   ```bash
   # Check all services are running
   docker-compose -f docker-compose.prod.yml ps

   # Check backend health
   curl http://localhost:8000/health

   # Check frontend
   curl http://localhost:3000
   ```

### Production Maintenance

#### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

#### Database Backup
```bash
# Backup
docker exec humansontology_db_prod pg_dump -U $DB_USER $DB_NAME > backup.sql

# Restore
docker exec -i humansontology_db_prod psql -U $DB_USER $DB_NAME < backup.sql
```

#### Update Deployment
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d

# Check for issues
docker-compose -f docker-compose.prod.yml logs -f
```

#### Scale Services (if needed)
```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Quick Start Commands

### Development

```bash
# Start
docker-compose -f docker-compose.dev.yml up --build

# Stop
docker-compose -f docker-compose.dev.yml down

# Clean restart
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Production

```bash
# Start
docker-compose -f docker-compose.prod.yml up --build -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Troubleshooting

### Backend fails with JWT_SECRET_KEY error

**Problem:** `JWT_SECRET_KEY must be changed from default value`

**Solution:**
```bash
# Generate new secret
openssl rand -hex 32

# Update .env file with generated secret
# Make sure it's different from the default value
```

### Database connection failed

**Problem:** Backend cannot connect to database

**Solution:**
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify credentials in .env match database configuration
```

### Frontend cannot reach backend

**Problem:** GraphQL endpoint not accessible

**Solution:**
1. Check CORS configuration in `.env`:
   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. Check backend is healthy:
   ```bash
   curl http://localhost:8000/health
   ```

3. Verify VITE_GRAPHQL_ENDPOINT in frontend matches backend URL

### Port already in use

**Problem:** Cannot start because port is occupied

**Solution:**
```bash
# Find what's using the port (example: 8000)
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Change port in .env
BACKEND_PORT=8001
```

### Out of disk space

**Problem:** Docker volumes filling up disk

**Solution:**
```bash
# Clean unused Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune

# See disk usage
docker system df
```

### Email not sending in development

**Problem:** Emails not visible

**Solution:**
1. Make sure MailPit is running:
   ```bash
   docker-compose -f docker-compose.dev.yml ps mailpit
   ```

2. Access MailPit UI: http://localhost:8025

3. Check backend SMTP configuration points to mailpit

### Database not seeding

**Problem:** No initial data in database

**Solution:**
1. Check SEED_DATABASE in .env:
   ```env
   SEED_DATABASE=true
   ```

2. Recreate database:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

## Security Best Practices

### Production Checklist

- [ ] All secrets are generated and unique
- [ ] JWT_SECRET_KEY is not the default value
- [ ] Database password is strong (32+ characters)
- [ ] Redis password is set (if exposed)
- [ ] DEBUG is set to False
- [ ] HTTPS is enabled with valid certificates
- [ ] CORS is configured with actual domain
- [ ] Sentry or error tracking is configured
- [ ] Regular backups are scheduled
- [ ] Firewall rules are configured
- [ ] Docker images are regularly updated
- [ ] Logs are monitored
- [ ] Resources (CPU/RAM) are monitored

## Environment Variables Reference

| Variable | Development | Production | Description |
|----------|------------|------------|-------------|
| `ENVIRONMENT` | development | production | Application environment |
| `DEBUG` | True | False | Enable debug mode |
| `JWT_SECRET_KEY` | Generated | Generated (must change!) | Secret for JWT tokens |
| `DB_PASSWORD` | Simple | Strong (32+ chars) | Database password |
| `REDIS_PASSWORD` | Empty | Set | Redis password |
| `SEED_DATABASE` | true | false | Seed initial data |
| `ALLOWED_ORIGINS` | localhost | Domain | CORS origins |
| `SMTP_HOST` | mailpit | SMTP server | Email server |
| `SENTRY_DSN` | Empty | Set | Error tracking |

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review environment variables
- Consult API docs: http://localhost:8000/docs
- Check health endpoints: http://localhost:8000/health
