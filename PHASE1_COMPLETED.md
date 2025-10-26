# Phase 1 Completed: UI Translations Seed Data

## ✅ Что было сделано

### 1. Создан скрипт seed_ui_concepts.py
**Файл:** `packages/backend/scripts/seed_ui_concepts.py`

**Функционал:**
- Создает 70+ UI-концептов с путями типа `ui/nav/dashboard`, `ui/button/login`, и т.д.
- Для каждого концепта создает Dictionary записи для 3 языков: English (en), Russian (ru), Spanish (es)
- Автоматически вычисляет depth и parent_id для иерархии концептов
- Проверяет существование UI-концептов перед созданием (идемпотентность)

**Охватываемые страницы:**
- ✅ Navigation / Header (10 элементов)
- ✅ Buttons (10 элементов)
- ✅ Home Page (12 элементов)
- ✅ Dashboard (4 элемента)
- ✅ Concepts Page (8 элементов)
- ✅ Languages Page (4 элемента)
- ✅ Dictionaries Page (3 элемента)
- ✅ Auth Pages (6 элементов)
- ✅ Common (13 элементов)

**Итого:** ~70 UI-концептов × 3 языка = ~210 переводов

### 2. Интеграция в seed_data.py
**Файл:** `packages/backend/scripts/seed_data.py`

Добавлен вызов `seed_ui_concepts(db)` в функцию `main()`, что обеспечивает автоматическую загрузку UI-переводов при инициализации базы данных.

---

## 🧪 Как протестировать

### Вариант 1: Через Docker (Рекомендуется)

```bash
# Остановить текущие контейнеры
docker-compose down -v

# Пересобрать и запустить с чистой БД
docker-compose up -d --build

# Проверить логи backend
docker-compose logs backend | grep "UI concepts"
# Должно появиться: "✓ Added 70 UI concepts with 210 translations"
```

### Вариант 2: Локально (если настроено окружение)

```bash
cd packages/backend

# Активировать виртуальное окружение (если есть)
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Запустить seed скрипт напрямую
python scripts/seed_ui_concepts.py

# ИЛИ запустить полный seed
python scripts/seed_data.py
```

---

## ✅ Проверка результатов

### 1. Через GraphQL Playground

Откройте: http://localhost:8000/graphql

**Query 1: Получить все UI-концепты**
```graphql
query GetUIConcepts {
  concepts(limit: 100) {
    id
    path
    depth
    dictionaries {
      language {
        code
      }
      name
    }
  }
}
```

**Query 2: Получить переводы для навигации (EN)**
```graphql
query GetNavTranslations {
  dictionaries(languageId: 2, limit: 20) {
    concept {
      path
    }
    name
    language {
      code
    }
  }
}
```
Примечание: `languageId: 2` это English (en). Для Russian используйте `languageId: 1`.

**Query 3: Поиск UI-концептов по path**
```graphql
query SearchUIConcepts {
  searchConcepts(query: "ui/nav") {
    path
    dictionaries {
      language {
        code
      }
      name
    }
  }
}
```

### 2. Через psql (если доступен)

```bash
# Подключиться к БД в контейнере
docker-compose exec db psql -U template_user -d templates

# Проверить количество UI-концептов
SELECT COUNT(*) FROM concepts WHERE path LIKE 'ui/%';
-- Должно быть ~70

# Проверить количество UI-переводов
SELECT COUNT(*)
FROM dictionaries d
JOIN concepts c ON d.concept_id = c.id
WHERE c.path LIKE 'ui/%';
-- Должно быть ~210 (70 концептов × 3 языка)

# Посмотреть примеры переводов для навигации
SELECT
  c.path,
  l.code as language,
  d.name as translation
FROM dictionaries d
JOIN concepts c ON d.concept_id = c.id
JOIN languages l ON d.language_id = l.id
WHERE c.path LIKE 'ui/nav/%'
ORDER BY c.path, l.code;

# Выход
\q
```

### 3. Проверить структуру данных

**Ожидаемая структура концептов:**
```
ui/
├── nav/
│   ├── dashboard
│   ├── concepts
│   ├── languages
│   ├── dictionaries
│   └── admin
├── button/
│   ├── login
│   ├── logout
│   ├── save
│   └── ...
├── home/
│   ├── title
│   ├── subtitle
│   └── ...
└── ...
```

---

## 📊 Ожидаемые результаты

После успешного seed должно быть создано:

- **Концепты (Concepts):**
  - Старые концепты (colors, animals, food, etc.): ~70
  - Новые UI-концепты: ~70
  - **Итого:** ~140 концептов

- **Словари (Dictionaries):**
  - Старые переводы: ~200-300
  - Новые UI-переводы: ~210
  - **Итого:** ~400-500 словарных записей

---

## 🐛 Troubleshooting

### Проблема: "UI concepts already exist, skipping..."
**Решение:** Это нормально, если вы запускаете seed повторно. Скрипт идемпотентен.

### Проблема: "Missing languages: ['es']"
**Решение:** Убедитесь что `seed_languages()` выполняется перед `seed_ui_concepts()`. В текущей версии это уже исправлено.

### Проблема: "ImportError: cannot import name 'seed_ui_concepts'"
**Решение:** Убедитесь что файл `packages/backend/scripts/seed_ui_concepts.py` существует и не содержит синтаксических ошибок.

### Проблема: Backend не стартует после изменений
**Решение:**
```bash
# Проверить логи
docker-compose logs backend

# Пересобрать контейнер
docker-compose down
docker-compose build backend --no-cache
docker-compose up -d
```

---

## 🎯 Следующие шаги (Phase 2)

После проверки, что seed работает корректно, переходим к Phase 2:

1. **Создать utility функции** (`packages/frontend/src/lib/utils/i18n.ts`)
   - Функция `t()` для получения перевода
   - Функция `dictionariesToMap()` для преобразования массива в объект

2. **Создать Houdini GraphQL query** для загрузки UI-переводов

3. **Обновить +layout.ts** для загрузки глобальных переводов

4. **Обновить AppHeader.svelte** для использования переводов

См. детали в `BACKLOG_SIMPLIFIED.MD`

---

## 📝 Примеры использования (Preview)

### Backend (GraphQL Query)
```graphql
query GetUITranslations($languageId: Int!) {
  dictionaries(languageId: $languageId, limit: 200) {
    concept {
      path
    }
    name
  }
}

# Variables:
{
  "languageId": 2  # English
}

# Response:
{
  "data": {
    "dictionaries": [
      {
        "concept": { "path": "ui/nav/dashboard" },
        "name": "Dashboard"
      },
      {
        "concept": { "path": "ui/button/login" },
        "name": "Login"
      },
      ...
    ]
  }
}
```

### Frontend (Future Implementation)
```svelte
<script>
  import { t } from '$lib/utils/i18n';
  import { page } from '$app/stores';

  const trans = $derived($page.data.globalTranslations || {});
</script>

<nav>
  <a href="/dashboard">
    {t(trans, 'ui/nav/dashboard', 'Dashboard')}
  </a>
  <button onclick={handleLogout}>
    {t(trans, 'ui/button/logout', 'Logout')}
  </button>
</nav>
```

---

## ✅ Checklist для завершения Phase 1

- [x] Создан файл `seed_ui_concepts.py`
- [x] Добавлено 70+ UI-концептов с переводами (EN, RU, ES)
- [x] Интегрировано в `seed_data.py`
- [ ] Протестировано через Docker
- [ ] Проверено через GraphQL Playground
- [ ] Проверено количество записей в БД

---

**Дата:** 2025-10-23
**Статус:** ✅ Phase 1 Backend Complete
**Следующий шаг:** Phase 2 - Frontend Integration
