# Quick Start Guide

## Development Environment (Recommended for First Run)

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd HumansOntology
   ```

2. **Use development environment:**
   ```bash
   # The .env file is already configured for development
   # with a generated JWT secret

   # Start all services
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs
   - GraphQL Playground: http://localhost:8000/graphql
   - MailPit (Email Testing): http://localhost:8025

4. **Stop the application:**
   ```bash
   # Press Ctrl+C in the terminal, then:
   docker-compose -f docker-compose.dev.yml down
   ```

### What's Included

- ✅ Frontend with hot reload
- ✅ Backend API with hot reload
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ MailPit for email testing
- ✅ Sample data seeded automatically

## Production Deployment

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Quick Production Setup

1. **Copy production example:**
   ```bash
   cp .env.prod.example .env.prod
   ```

2. **Generate secrets:**
   ```bash
   openssl rand -hex 32  # For JWT_SECRET_KEY
   ```

3. **Edit `.env.prod`** with your values

4. **Deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## Common Issues

### Port Already in Use

If you get a port conflict error:

**Option 1: Change ports in `.env`**
```env
BACKEND_PORT=8001
FRONTEND_PORT=5174
```

**Option 2: Stop conflicting service**
```bash
# Windows - Find what's using port 8000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Database Issues

**Clean restart:**
```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Need Help?

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed documentation and troubleshooting.

## Default Credentials

After seeding, you can log in with:

- **Email:** admin@example.com
- **Password:** admin123

⚠️ **Change these credentials immediately in production!**

## Project Structure

```
HumansOntology/
├── packages/
│   ├── backend/         # FastAPI backend
│   └── frontend/        # SvelteKit frontend
├── docker-compose.yml           # Legacy (don't use)
├── docker-compose.dev.yml       # Development environment
├── docker-compose.prod.yml      # Production environment
├── .env                 # Current environment config (dev)
├── .env.dev            # Development config
├── .env.prod.example   # Production config template
├── DEPLOYMENT.md       # Full deployment guide
└── QUICK_START.md     # This file
```

## Next Steps

1. **Explore the API:** http://localhost:8000/docs
2. **Test email:** Create account and check http://localhost:8025
3. **Review code:** Browse `packages/backend` and `packages/frontend`
4. **Customize:** Update configurations as needed
5. **Deploy:** Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for production

## Support

- 📚 API Documentation: http://localhost:8000/docs
- 🎮 GraphQL Playground: http://localhost:8000/graphql
- 📧 Email Testing: http://localhost:8025
- 🚀 Deployment Guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
