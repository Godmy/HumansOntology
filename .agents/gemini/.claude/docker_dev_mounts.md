# Настройка монтирования томов для ускорения разработки в Docker

При разработке с использованием Docker часто возникает необходимость вносить изменения в код и сразу же видеть их в работающем контейнере, не пересобирая образ каждый раз. Это достигается с помощью монтирования томов (volumes), которые позволяют синхронизировать файлы между хост-машиной и контейнером.

В этом документе описаны подходы к настройке монтирования томов для dev-сборок, с примерами для бэкенда на Python и фронтенда на Svelte/Node.js, исходя из структуры вашего проекта `HumansOntology`.

---

## 1. Основная концепция монтирования томов

Монтирование тома позволяет связать директорию на вашей хост-машине с директорией внутри контейнера. Любые изменения, сделанные в этой директории на хосте, будут немедленно видны в контейнере, и наоборот.

**Синтаксис:**

- `docker run -v /путь/на/хосте:/путь/в/контейнере ...`
- В `docker-compose.yml`: в секции `volumes` для каждого сервиса.

---

## 2. Настройка в `docker-compose.dev.yml`

Для dev-сборок рекомендуется использовать отдельный `docker-compose.dev.yml` файл, который расширяет основной `docker-compose.yml` и добавляет специфичные для разработки настройки, такие как монтирование томов и включение режимов горячей перезагрузки.

Предположим, у вас есть базовый `docker-compose.yml` и вы создадите `docker-compose.dev.yml`.

**Пример `docker-compose.yml` (базовый):**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env.example

  frontend:
    build:
      context: ./packages/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env.example
```

**Пример `docker-compose.dev.yml` (для разработки):**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile.dev # Используем Dockerfile.dev для dev-сборки
    volumes:
      - ./packages/backend:/app # Монтируем исходники бэкенда
      - /app/venv # Исключаем venv, если он создается внутри контейнера
      - /app/__pycache__ # Исключаем __pycache__
    command: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload # Включаем hot-reload

  frontend:
    build:
      context: ./packages/frontend
      dockerfile: Dockerfile.dev # Используем Dockerfile.dev для dev-сборки
    volumes:
      - ./packages/frontend:/app # Монтируем исходники фронтенда
      - /app/node_modules # Исключаем node_modules, чтобы они не перезаписывались с хоста
    command: npm run dev -- --host 0.0.0.0 --port 3000 # Включаем dev-сервер с hot-reload
```

**Запуск dev-сборки:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

---

## 3. Детальная настройка для сервисов

### 3.1. Бэкенд (Python - `packages/backend`)

Для Python-бэкенда на FastAPI/Flask обычно используется режим перезагрузки (hot-reload), который автоматически перезапускает сервер при изменении файлов.

- **`Dockerfile.dev` (пример):**
  Создайте отдельный `Dockerfile.dev` в `packages/backend`, который может отличаться от продакшн-версии. Например, он может устанавливать dev-зависимости и не копировать код, так как он будет монтироваться.

  ```dockerfile
  # packages/backend/Dockerfile.dev
  FROM python:3.9-slim-buster

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Код не копируем, он будет монтироваться

  CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  ```

- **`volumes` в `docker-compose.dev.yml`:**
  ```yaml
  volumes:
    - ./packages/backend:/app # Монтируем всю директорию с исходниками
    - /app/venv # Исключаем виртуальное окружение, если оно создается внутри контейнера
    - /app/__pycache__ # Исключаем кэш Python
  ```
  **Пояснение:**
  - `./packages/backend:/app`: Это основное монтирование. Все файлы из вашей локальной папки `packages/backend` будут доступны в `/app` внутри контейнера.
  - `/app/venv` и `/app/__pycache__`: Эти строки используются для **исключения** определенных директорий из монтирования. Если `venv` или `__pycache__` создаются внутри контейнера, и вы не хотите, чтобы они перезаписывались с хоста (или чтобы хост-версии мешали контейнерным), их можно указать как анонимные тома. Docker создаст для них пустые тома, которые "закроют" соответствующие директории на хосте.

- **`command`:**
  ```yaml
  command: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
  ```
  Используйте команду, которая запускает ваш сервер в режиме разработки с автоматической перезагрузкой (например, `--reload` для Uvicorn).

### 3.2. Фронтенд (Svelte/Node.js - `packages/frontend`)

Для фронтенда на Svelte (или любом другом фреймворке на Node.js) также важен hot-reload и правильное управление `node_modules`.

- **`Dockerfile.dev` (пример):**
  Создайте отдельный `Dockerfile.dev` в `packages/frontend`.

  ```dockerfile
  # packages/frontend/Dockerfile.dev
  FROM node:18-alpine

  WORKDIR /app

  COPY package.json yarn.lock* ./ # Копируем только файлы зависимостей
  RUN yarn install --frozen-lockfile # Устанавливаем зависимости

  # Код не копируем, он будет монтироваться

  CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
  ```

- **`volumes` в `docker-compose.dev.yml`:**
  ```yaml
  volumes:
    - ./packages/frontend:/app # Монтируем всю директорию с исходниками
    - /app/node_modules # Исключаем node_modules
  ```
  **Пояснение:**
  - `./packages/frontend:/app`: Монтирование исходников фронтенда.
  - `/app/node_modules`: **Критично для Node.js проектов.** Если вы монтируете всю директорию `packages/frontend`, то `node_modules` с хоста (если они там есть) перезапишут `node_modules` внутри контейнера. Это может привести к проблемам совместимости (например, если на хосте Windows, а в контейнере Linux). Исключая `node_modules` таким образом, вы гарантируете, что Docker будет использовать `node_modules`, установленные внутри контейнера (как это сделано в `Dockerfile.dev`).

- **`command`:**
  ```yaml
  command: npm run dev -- --host 0.0.0.0 --port 3000
  ```
  Запускает dev-сервер SvelteKit (или Vite) с hot-reload.

---

## 4. Важные замечания

- **Абсолютные пути:** Всегда используйте абсолютные пути для монтирования томов на хосте (например, `./packages/backend` относительно корня `docker-compose.yml`).
- **Права доступа:** Иногда могут возникать проблемы с правами доступа к файлам между хостом и контейнером. Убедитесь, что пользователь внутри контейнера имеет необходимые права на чтение/запись в монтируемые директории.
- **`.dockerignore`:** Убедитесь, что ваш `.dockerignore` в `packages/backend` и `packages/frontend` правильно настроен, чтобы не копировать ненужные файлы в продакшн-образы.
- **Кэширование Docker:** При использовании `docker-compose up --build` Docker будет пересобирать образы. Если вы хотите избежать пересборки, но обновить код, используйте `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` (без `--build`), но только если `Dockerfile.dev` не менялся.
- **Производительность:** На некоторых операционных системах (особенно macOS и Windows с WSL 1) производительность монтированных томов может быть ниже, чем нативная файловая система. WSL 2 на Windows значительно улучшает эту ситуацию.

Используя эти подходы, вы сможете значительно ускорить цикл разработки, позволяя мгновенно видеть изменения кода без постоянной пересборки Docker-образов.