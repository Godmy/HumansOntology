# HumanOntology

Application of Mathematical Chaos Theory Concepts for the Construction of a Physical Core Attractor Catalog Using Morphological Analysis

## Структура проекта

Проект состоит из двух submodules:
- `packages/backend` - Backend API на Python (FastAPI + GraphQL)
- `packages/frontend` - Frontend на SvelteKit

## Быстрый старт

### Предварительные требования

- Docker
- Docker Compose
- Git

### Установка и запуск

1. Клонируйте репозиторий с submodules:
```bash
git clone --recursive https://github.com/your-username/HumansOntology.git
cd HumansOntology
```

2. Если вы уже клонировали репозиторий без submodules:
```bash
git submodule init
git submodule update
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Отредактируйте `.env` файл (особенно важно изменить `JWT_SECRET_KEY` для production):
```bash
nano .env
```

5. Запустите проект:

**Production режим:**
```bash
docker-compose up -d
```

**Development режим (с MailPit для тестирования email):**
```bash
docker-compose --profile dev up -d
```

### Доступные сервисы

После запуска будут доступны:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
  - Доступны примеры запросов: http://localhost:8000/graphql/examples
  - Для разработки можно получить тестовый токен: http://localhost:8000/graphql/test-user-login (только в dev-окружении)
- **Backend Health Check**: http://localhost:8000/health
- **MailPit Web UI** (только dev): http://localhost:8025

### Управление контейнерами

```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache

# Перезапуск отдельного сервиса
docker-compose restart backend
```

### База данных

При первом запуске база данных автоматически инициализируется и заполняется тестовыми данными (если `SEED_DATABASE=true`).

**Тестовые пользователи:**
- `admin / Admin123!` - Администратор
- `moderator / Moderator123!` - Модератор
- `editor / Editor123!` - Редактор
- `testuser / User123!` - Обычный пользователь

### Миграции базы данных

```bash
# Применить миграции
docker-compose exec backend alembic upgrade head

# Создать новую миграцию
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Откатить последнюю миграцию
docker-compose exec backend alembic downgrade -1
```

### Обновление submodules

```bash
# Обновить все submodules до последней версии
git submodule update --remote

# Обновить конкретный submodule
git submodule update --remote packages/backend
git submodule update --remote packages/frontend
```

## Разработка

### Backend

Полная документация backend: [packages/backend/README.md](packages/backend/README.md)

Технологический стек:
- Python 3.11
- FastAPI + Starlette
- Strawberry GraphQL
- SQLAlchemy
- PostgreSQL
- Redis

### Frontend

Полная документация frontend: [packages/frontend/README.md](packages/frontend/README.md)

Технологический стек:
- SvelteKit
- TypeScript
- Houdini (GraphQL client)
- Vite

## Документация

Вся основная документация по проекту собрана в директории `/docs`.

- [**Главная страница документации**](./docs/index.md) - отправная точка для навигации по всем документам.
- [**Обзор архитектуры**](./docs/ARCHITECTURE_OVERVIEW.md) - высокоуровневое описание всех компонентов системы.

## Конфигурация

Все настройки управляются через переменные окружения в файле `.env`. Смотрите `.env.example` для полного списка доступных опций.

### Важные настройки для production:

1. **JWT_SECRET_KEY** - ОБЯЗАТЕЛЬНО измените на уникальный ключ
2. **DB_PASSWORD** - Установите безопасный пароль для базы данных
3. **SMTP_*** - Настройте реальный SMTP сервер для отправки email
4. **SENTRY_DSN** - Настройте Sentry для мониторинга ошибок (опционально)
5. **ALLOWED_ORIGINS** - Укажите разрешенные домены для CORS

## Лицензия

См. файл [LICENSE](LICENSE)

## Разработчики

- Backend: https://github.com/Godmy/backend
- Frontend: https://github.com/Godmy/frontend