# 🌍 Multilingual UI System - Quick Start

## ✅ Что готово

**Backend:** 70+ UI переводов для EN, RU, ES автоматически загружаются в БД
**Frontend:** Полная инфраструктура i18n + Home Page, Header, Navigation переведены
**Прогресс:** ~70% базовой функциональности

---

## 🚀 Быстрый старт

### 1. Запустить проект
```bash
# Пересоздать БД с UI переводами
docker-compose down -v
docker-compose up -d --build

# Проверить логи
docker-compose logs backend | grep "UI concepts"
# Должно: "✓ Added 70 UI concepts with 210 translations"
```

### 2. Открыть приложение
```bash
open http://localhost:5173
```

### 3. Переключить язык
1. В правом верхнем углу найти **Language Switcher**
2. Выбрать **Russian (ru)** или **Español (es)**
3. Навигация изменится на выбранный язык
4. Перезагрузить страницу (в текущей версии)

---

## 📁 Ключевые файлы

### Backend:
- `packages/backend/scripts/seed_ui_concepts.py` - 70+ UI переводов
- `packages/backend/scripts/seed_data.py` - интеграция seed

### Frontend:
- `packages/frontend/src/lib/utils/i18n.ts` - 8 функций для работы с переводами
- `packages/frontend/src/routes/+layout.gql` - GraphQL query
- `packages/frontend/src/routes/+layout.ts` - load function
- `packages/frontend/src/routes/+page.svelte` - пример использования (Home Page)

### Документация:
- `MULTILINGUAL_UI_IMPLEMENTATION_SUMMARY.md` - полный обзор
- `PHASE1_COMPLETED.md` - Backend инструкции
- `PHASE2_COMPLETED.md` - Frontend API
- `PHASE3_COMPLETED.md` - Pages checklist
- `BACKLOG_SIMPLIFIED.MD` - план работ

---

## 🎯 Как использовать

### В любом компоненте:

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { t } from '$lib/utils/i18n';

  // Получить переводы из layout
  const trans = $derived($page.data.translations || {});
</script>

<!-- Использовать переводы -->
<h1>{t(trans, 'ui/home/title', 'Home')}</h1>
<button>{t(trans, 'ui/button/save', 'Save')}</button>
```

---

## ✅ Что переведено

### Полностью:
- ✅ Home Page (hero, features, CTA, footer)
- ✅ AppHeader (navigation, buttons)
- ✅ LanguageSwitcher

### Частично:
- ⏳ Dashboard (title, welcome, stats)

### Требуется обновить:
- ❌ Concepts, Languages, Dictionaries Pages
- ❌ Auth Pages (Login, Register, Forgot Password)

См. `PHASE3_COMPLETED.md` для инструкций

---

## 🧪 Тестирование через GraphQL

```bash
open http://localhost:8000/graphql
```

```graphql
# Получить все UI переводы для русского языка
query {
  dictionaries(languageId: 1, limit: 300) {
    concept {
      path
    }
    name
  }
}

# Получить для английского
query {
  dictionaries(languageId: 2, limit: 300) {
    concept {
      path
    }
    name
  }
}
```

---

## 📊 Доступные языки

| ID | Code | Name |
|----|------|------|
| 1 | ru | Русский |
| 2 | en | English |
| 3 | es | Español |

---

## 💡 Добавить новый перевод

### 1. Добавить в seed data:
Открыть `packages/backend/scripts/seed_ui_concepts.py`:

```python
UI_TRANSLATIONS = {
    'ui/your/new/key': {
        'en': 'English text',
        'ru': 'Русский текст',
        'es': 'Texto español'
    },
    # ...
}
```

### 2. Пересоздать БД:
```bash
docker-compose down -v
docker-compose up -d
```

### 3. Использовать в коде:
```svelte
{t(trans, 'ui/your/new/key', 'Fallback')}
```

---

## 🐛 Troubleshooting

### Переводы не загружаются
```bash
# Проверить backend
docker-compose logs backend

# Проверить query в GraphQL
open http://localhost:8000/graphql
```

### Переводы не меняются при переключении языка
- В текущей версии требуется перезагрузка страницы
- Реактивное переключение - Phase 4 (TODO)

### "Cannot read translations of undefined"
Добавить проверку в компоненте:
```typescript
const trans = $derived($page.data?.translations || {});
```

---

## 📚 Документация

**Полный обзор:** `MULTILINGUAL_UI_IMPLEMENTATION_SUMMARY.md`

**API Reference:**
- `t(translations, key, fallback)` - получить перевод
- `tParams(translations, key, params, fallback)` - с параметрами
- `dictionariesToMap(dictionaries)` - преобразовать массив
- `hasTranslation(translations, key)` - проверить наличие
- `mergeTranslations(...arrays)` - объединить

**Примеры:** `packages/frontend/src/routes/+page.svelte`

---

## 🎯 Следующие шаги

1. **Завершить Phase 3** - обновить оставшиеся 6 страниц (2-3 часа)
2. **Phase 4 (опционально)** - реактивное переключение без перезагрузки
3. **Добавить больше языков** - FR, DE, IT, JA, ZH, AR
4. **Enhancements** - кэширование, admin UI, CLI tools

См. `MULTILINGUAL_UI_IMPLEMENTATION_SUMMARY.md` для деталей

---

**Статус:** ✅ Ready to Use
**Версия:** 1.0
**Дата:** 2025-10-23
