# HumanOntology Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Directory Structure](#directory-structure)
5. [Installation and Setup](#installation-and-setup)
6. [Configuration](#configuration)
7. [Development](#development)
8. [Multilingual UI System](#multilingual-ui-system)
9. [Database and Migrations](#database-and-migrations)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

## Project Overview

The HumanOntology project is a sophisticated application that applies Mathematical Chaos Theory Concepts for the Construction of a Physical Core Attractor Catalog Using Morphological Analysis. The project is divided into two main components: a backend API built with Python/FastAPI and a frontend built with SvelteKit.

### Key Features
- Backend API using Python, FastAPI, and GraphQL
- Frontend using SvelteKit and TypeScript
- Multilingual UI system with support for EN, RU, ES languages
- Morphological analysis capabilities
- User authentication and authorization system
- Database management with PostgreSQL
- Caching with Redis

## Architecture

The system follows a microservices architecture pattern with a clear separation between the frontend and backend:

- **Backend**: Python-based service using FastAPI for REST and GraphQL APIs
- **Frontend**: SvelteKit application that consumes the backend APIs
- **Database**: PostgreSQL for persistent data storage
- **Cache**: Redis for caching and session storage
- **Email**: MailPit for development email testing
- **Authentication**: JWT-based authentication with refresh tokens

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI + Starlette
- **GraphQL**: Strawberry GraphQL
- **Database**: SQLAlchemy with PostgreSQL
- **Authentication**: JWT tokens
- **Caching**: Redis
- **Migrations**: Alembic
- **Email**: SMTP with MailPit for development

### Frontend
- **Framework**: SvelteKit
- **Language**: TypeScript
- **GraphQL Client**: Houdini
- **Build Tool**: Vite
- **Styling**: Tailwind CSS or similar

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment**: Docker Compose for local, with production deployment options

## Directory Structure

```
HumanOntology/
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── README.md
├── BACKLOG.MD
├── BACKLOG_SIMPLIFIED.MD
├── MULTILINGUAL_UI_IMPLEMENTATION_SUMMARY.md
├── MULTILINGUAL_UI_README.md
├── PHASE1_COMPLETED.md
├── PHASE2_COMPLETED.md
├── PHASE3_COMPLETED.md
├── DOCUMENTATION.md (this file)
├── packages/
│   ├── backend/
│   │   ├── app.py
│   │   ├── alembic/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── scripts/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/
│       ├── src/
│       ├── static/
│       ├── package.json
│       ├── svelte.config.js
│       ├── tsconfig.json
│       └── Dockerfile
└── parser/
```

## Installation and Setup

### Prerequisites
- Docker
- Docker Compose
- Git

### Installation Steps

1. Clone the repository with submodules:
   ```bash
   git clone --recursive https://github.com/your-username/HumansOntology.git
   cd HumansOntology
   ```

2. If you already cloned without submodules:
   ```bash
   git submodule init
   git submodule update
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file (especially change `JWT_SECRET_KEY` for production):
   ```bash
   nano .env
   ```

5. Run the project using Docker Compose:
   
   **For Production:**
   ```bash
   docker-compose up -d
   ```
   
   **For Development (with MailPit):**
   ```bash
   docker-compose --profile dev up -d
   ```

### Available Services
After starting the services, the following endpoints will be available:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **Backend Health Check**: http://localhost:8000/health
- **MailPit Web UI** (development only): http://localhost:8025

## Configuration

### Environment Variables

The application is configured through environment variables defined in the `.env` file. Key variables include:

- `DB_*`: Database connection settings (host, port, name, user, password)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (change for production)
- `REDIS_*`: Redis connection settings
- `SMTP_*`: Email configuration
- `ALLOWED_ORIGINS`: CORS allowed origins
- `SEED_DATABASE`: Whether to seed the database with test data
- `VITE_*`: Frontend-specific variables

### Important Production Settings

1. **JWT_SECRET_KEY** - MUST change to a unique key in production
2. **DB_PASSWORD** - Set a secure database password
3. **SMTP_*** - Configure real SMTP server for production email
4. **SENTRY_DSN** - Set up Sentry for error monitoring (optional)
5. **ALLOWED_ORIGINS** - Specify allowed domains for CORS

## Development

### Backend Development

The backend is located in `packages/backend/` and uses Python 3.11 with FastAPI.

Key technologies:
- FastAPI + Strawberry GraphQL
- SQLAlchemy ORM
- Alembic for database migrations

### Frontend Development

The frontend is located in `packages/frontend/` and uses SvelteKit with TypeScript.

Key technologies:
- SvelteKit framework
- TypeScript
- Houdini GraphQL client
- Vite build tool

### Docker Compose Management

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop with volume removal
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Restart specific service
docker-compose restart backend
```

### Submodule Management

```bash
# Update all submodules to latest version
git submodule update --remote

# Update specific submodule
git submodule update --remote packages/backend
git submodule update --remote packages/frontend
```

## Multilingual UI System

The project includes a comprehensive multilingual UI system supporting English, Russian, and Spanish.

### Key Components

- Backend: UI translations seeded into the database
- Frontend: i18n utilities and GraphQL queries for loading translations
- Language switcher component

### Implementation Details

1. **Backend Seed Data**: 70+ UI concepts with ~210 translations across 3 languages
2. **Frontend i18n Utilities**: 8 functions for translation handling
3. **GraphQL Integration**: Query for fetching UI translations by language ID
4. **SvelteKit Integration**: Translations loaded via layout load function

### Usage in Components

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { t } from '$lib/utils/i18n';

  // Get translations from layout
  const trans = $derived($page.data.translations || {});
</script>

<!-- Use translations -->
<h1>{t(trans, 'ui/home/title', 'Home')}</h1>
<button>{t(trans, 'ui/button/save', 'Save')}</button>
```

### Adding New Translations

1. Add to the seed data in `packages/backend/scripts/seed_ui_concepts.py`
2. Rebuild the database with `docker-compose down -v && docker-compose up -d`
3. Use the new translation key in components

## Database and Migrations

The project uses PostgreSQL as its primary database with SQLAlchemy as the ORM and Alembic for migrations.

### Database Operations

```bash
# Apply migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogen -m "Description"

# Rollback last migration
docker-compose exec backend alembic downgrade -1
```

### Seeding Data

On first run, the database is automatically initialized and populated with test data if `SEED_DATABASE=true`.

Test users:
- `admin / Admin123!` - Administrator
- `moderator / Moderator123!` - Moderator
- `editor / Editor123!` - Editor
- `testuser / User123!` - Regular user

## Testing

### Backend Testing

Backend tests are located in the `tests/` directory in the backend package.

### Frontend Testing

The frontend includes both unit tests and end-to-end tests:

- Unit tests: Located in the frontend package
- E2E tests: Using Playwright, located in `e2e/` directory

## Deployment

### Docker Compose Production

For production deployment, use the following:

```bash
docker-compose up -d --build
```

Make sure to update the `.env` file with production settings before deployment.

### Environment-Specific Configurations

- Development: Enabled MailPit for email testing (`--profile dev`)
- Production: Optimized for performance with minimal services

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Ensure the database service is running and credentials are correct
2. **Frontend Cannot Connect to Backend**: Check that the backend service is running and the API endpoint is correct
3. **Translation Issues**: Verify the seed process completed and the UI concepts were loaded

### Log Checking

```bash
# Check backend logs
docker-compose logs backend

# Check frontend logs
docker-compose logs frontend

# Check database logs
docker-compose logs db
```

### Debugging the Multilingual System

```bash
# Check if UI concepts were seeded
docker-compose logs backend | grep "UI concepts"

# Check GraphQL for translations
open http://localhost:8000/graphql
```

### Resetting the Environment

```bash
# Stop and remove containers and volumes
docker-compose down -v

# Rebuild everything
docker-compose up -d --build
```

## License

This project is licensed under the terms in the LICENSE file.