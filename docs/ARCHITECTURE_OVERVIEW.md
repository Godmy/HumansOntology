# HumanOntology Project Architecture

## Overview

The HumanOntology project is a sophisticated application that applies Mathematical Chaos Theory Concepts for the Construction of a Physical Core Attractor Catalog Using Morphological Analysis. It follows a microservices architecture with a clear separation between the frontend and backend components.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              Client (Browser)                                   │
│                                                                                 │
│     ┌───────────────────────────────────────────────────────┐    │
│     │                           Frontend                                   │    │
│     │                        (SvelteKit App)                               │    │
│     │                                                                      │    │
│     │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │    │
│     │  │ AppHeader       │    │ Pages           │    │ Components      │   │    │
│     │  │ (Nav, LoginBtn) │    │ (+layout.svelte,│    │ (Language       │   │    │
│     │  │                 │    │ +page.svelte,   │    │ Switcher, etc.) │   │    │
│     │  │                 │    │ dashboard/,     │    │                 │   │    │
│     │  │                 │    │ concepts/,      │    │                 │   │    │
│     │  │                 │    │ languages/,     │    │                 │   │    │
│     │  │                 │    │ dictionaries/)  │    │                 │   │    │
│     │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │    │
│     │                                                                      │    │
│     │  ┌───────────────────────────────────────────────────────┐ │    │
│     │  │                    Frontend Services                            │ │    │
│     │  │                                                                 │ │    │
│     │  │  ┌──────────────┐    ┌──────────────┐   ┌─────────────────┐ │ │    │
│     │  │  │ i18n.ts        │    │ LanguageStore  │   │ GraphQL Client  │ │ │    │
│     │  │  │ (Translation   │    │ (Svelte Store  │   │ (Houdini)       │ │ │    │
│     │  │  │ functions)     │    │ for language   │   │                 │ │ │    │
│     │  │  │                │    │ selection)     │   │                 │ │ │    │
│     │  │  └──────────────┘    └──────────────┘   └─────────────────┘ │ │    │
│     │  └───────────────────────────────────────────────────────┘ │    │
│     └───────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/GraphQL Requests
                                    │
┌───────────────────────────────────────────────────────────────────────────┐
│                              Server Infrastructure                              │
│                                                                                 │
│     ┌──────────────────────────────────────────────────────┐     │
│     │                           Backend API                               │     │
│     │                        (Python FastAPI)                             │     │
│     │                                                                     │     │
│     │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │     │
│     │  │ Core            │    │ Authentication  │    │ Languages       │  │     │
│     │  │ (Database,      │    │ (Users, Roles,  │    │ (Concepts,      │  │     │
│     │  │ Email, Redis,   │    │ Permissions,    │    │ Dictionaries,   │  │     │
│     │  │ File Storage)   │    │ OAuth)          │    │ Translations)   │  │     │
│     │  └─────────────────┘    └─────────────────┘    └─────────────────┘  │     │
│     │                                                                     │     │
│     │  ┌───────────────────────────────────────────────────────┐ │     │
│     │  │                     GraphQL Schema                             │ │     │
│     │  │                                                                │ │     │
│     │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │     │
│     │  │  │ User Queries    │  │ Language        │  │ File Operations │ │ │     │
│     │  │  │ (Get user data, │  │ (Concepts,      │  │ (Upload,        │ │ │     │
│     │  │  │ Update profile) │  │ Dictionaries,   │  │ Download,       │ │ │     │
│     │  │  └─────────────────┘  │ Translations)   │  │ Thumbnails)     │ │ │     │
│     │  │                       └─────────────────┘  └─────────────────┘ │ │     │
│     │  └───────────────────────────────────────────────────────┘ │     │
│     └──────────────────────────────────────────────────────┘     │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │ PostgreSQL      │    │ Redis           │    │ MailPit         │              │
│  │ (Main Data &    │    │ (Caching,       │    │ (Email Testing  │              │
│  │ UI Translations)│    │ Sessions)       │    │ in Dev)         │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘              │
└───────────────────────────────────────────────────────────────────────────┘

## Component Breakdown

### 1. Frontend (SvelteKit Application)

The frontend serves as the user interface layer of the application:

- **Framework**: SvelteKit
- **Language**: TypeScript
- **GraphQL Client**: Houdini
- **Build Tool**: Vite

**Key Components:**
- **AppHeader**: Contains navigation and user controls
- **Pages**: Individual route handlers (+page.svelte files)
- **Components**: Reusable UI elements
- **i18n System**: Internationalization functionality with support for EN, RU, ES
- **LanguageStore**: Svelte store for managing language selection
- **GraphQL Queries**: Client-side GraphQL operations

### 2. Backend (Python/FastAPI API)

The backend provides the business logic and API endpoints:

#### Core Module
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Redis Client**: For caching and session management
- **Email Service**: For sending notifications and verification emails
- **File Storage**: For handling file uploads and storage
- **Models**: Base models and audit logging
- **Services**: File and audit service logic

#### Authentication Module
- **User Management**: Registration, login, password reset
- **Role-Based Access**: Role and permission management
- **OAuth Integration**: Google and Telegram OAuth
- **JWT Authentication**: Secure token-based authentication
- **Profile Management**: User profile information

#### Languages Module
- **Concept System**: Hierarchical concept management for morphological analysis
- **Dictionary System**: Multilingual concept translations
- **Language Support**: Management of supported languages

### 3. Infrastructure Components

#### Databases
- **PostgreSQL**: Primary database for application data and UI translations
- **Redis**: Caching layer and session storage

#### Services
- **MailPit**: Email testing service (development only)
- **Nginx**: Optional reverse proxy (in production)

## Data Flow

### Standard Request Flow
```
Client Request (GraphQL/REST)
         ↓
Frontend (SvelteKit)
         ↓
GraphQL Client (Houdini)
         ↓
Backend API (FastAPI)
         ↓
GraphQL Schema Layer
         ↓
Service Layer (Business Logic)
         ↓
Data Layer (SQLAlchemy Models)
         ↓
PostgreSQL Database
         ↓
Response Flow (Reverse Order)
```

### Authentication Flow
```
User Login Attempt
         ↓
Frontend (Login Form)
         ↓
GraphQL Mutation: login
         ↓
Auth Schema Layer
         ↓
Auth Service (Validate Credentials)
         ↓
JWT Token Generation
         ↓
Response with Token
         ↓
Frontend (Store JWT in localStorage)
```

## Architecture Principles

### 1. Modular Structure
- Each module (core, auth, languages) contains its own models, schemas, and services
- Clear separation of concerns between different functional areas
- Reusable services that are independent of the API layer

### 2. Layered Architecture
- Presentation Layer: Frontend (SvelteKit components)
- API Layer: GraphQL schemas
- Service Layer: Business logic
- Data Layer: Database models

### 3. Clean Architecture
- Business logic is independent of external frameworks
- External components (API, database) are adapters to the core business logic
- Dependency inversion - high-level modules don't depend on low-level modules

### 4. Scalability
- Containerized deployment with Docker
- Stateless application services
- Caching layer with Redis
- Horizontal scaling capabilities

## Technologies Used

### Backend Technologies
- **Language**: Python 3.11
- **Framework**: FastAPI for API endpoints
- **GraphQL**: Strawberry GraphQL
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Caching**: Redis
- **Migrations**: Alembic
- **Email**: SMTP with MailPit for development

### Frontend Technologies
- **Framework**: SvelteKit
- **Language**: TypeScript
- **State Management**: Svelte stores
- **GraphQL Client**: Houdini
- **Build Tool**: Vite
- **Styling**: Tailwind CSS or similar

### Infrastructure Technologies
- **Containerization**: Docker & Docker Compose
- **Development Tool**: MailPit for email testing
- **Production Deployment**: Docker Compose

## Database Schema Overview

### Core Tables
- **users**: User accounts with authentication data
- **roles**: User roles for access control
- **permissions**: Permission definitions
- **user_profiles**: Extended user profile information
- **files**: File metadata and storage information
- **audit_logs**: System activity logs

### Language/Translation Tables
- **languages**: Supported languages (en, ru, es, etc.)
- **concepts**: Hierarchical concept definitions
- **dictionaries**: Language-specific translations of concepts
- **oauth_connections**: External OAuth provider links

## Security Considerations

1. **Authentication**: JWT-based authentication with refresh tokens
2. **Authorization**: Role-based access control with permissions
3. **Input Validation**: Server-side validation on all API endpoints
4. **Database Security**: Parameterized queries to prevent SQL injection
5. **Transport Security**: HTTPS in production deployments
6. **Password Security**: Bcrypt hashing with salt
7. **Rate Limiting**: Implemented with Redis for API protection

## Deployment Architecture

### Development Environment
- Docker Compose with hot-reload capabilities
- All services running in containers
- MailPit for email testing
- Development-specific configurations

### Production Environment
- Optimized Docker images
- External PostgreSQL instance (recommended)
- Redis for caching and sessions
- Reverse proxy (Nginx) for SSL termination
- Production-specific security configurations

## Scaling Considerations

### Horizontal Scaling
- Stateless API services can be load-balanced
- Database connection pooling
- Redis-based session storage

### Database Scaling
- Primary/replica setup for PostgreSQL
- Read replicas for query distribution
- Connection pooling

### Caching Strategy
- Redis for session storage
- Application-level caching
- CDN for static assets (not implemented yet)