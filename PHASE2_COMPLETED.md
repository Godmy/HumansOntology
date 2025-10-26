# Phase 2 Completed: Frontend Integration - Header & Navigation

## ✅ Что было сделано

### 1. Созданы i18n utility функции
**Файл:** `packages/frontend/src/lib/utils/i18n.ts`

**Функции:**
- `t(translations, key, fallback)` - получить перевод по ключу
- `tParams(translations, key, params, fallback)` - перевод с интерполяцией параметров
- `dictionariesToMap(dictionaries)` - преобразовать массив Dictionary в объект
- `hasTranslation(translations, key)` - проверить наличие перевода
- `getTranslationsByPrefix(translations, prefix)` - получить переводы по префиксу
- `mergeTranslations(...arrays)` - объединить несколько объектов переводов
- `findMissingTranslations(translations, requiredKeys)` - найти отсутствующие переводы
- `createNamespaceT(translations, namespace)` - создать namespace функцию

**Экспорт:** Добавлен в `packages/frontend/src/lib/utils/index.ts`

---

### 2. Создан GraphQL query для загрузки UI-переводов
**Файл:** `packages/frontend/src/routes/+layout.gql`

```graphql
query GetUITranslations($languageId: Int!) {
  dictionaries(languageId: $languageId, limit: 300) {
    concept {
      path
    }
    name
  }
}
```

---

### 3. Создан +layout.ts с load function
**Файл:** `packages/frontend/src/routes/+layout.ts`

**Функционал:**
- Загружает все UI-переводы при загрузке layout
- Использует `languageStore` для определения текущего языка
- Преобразует массив в Map объект через `dictionariesToMap()`
- Возвращает `translations` доступные во всех дочерних страницах через `$page.data.translations`

---

### 4. Обновлен AppHeader.svelte
**Файл:** `packages/frontend/src/lib/components/AppHeader.svelte`

**Изменения:**
- Импортирован `t` из `$lib/utils/i18n`
- Получает переводы из `$page.data.translations`
- Заменены все hardcoded тексты на вызовы `t()`:
  - ✅ Navigation links: Dashboard, Concepts, Languages, Dictionaries
  - ✅ Buttons: Logout, Sign in, Get Started

---

### 5. Обновлен LanguageSwitcher.svelte
**Файл:** `packages/frontend/src/lib/components/LanguageSwitcher.svelte`

**Изменения:**
- Импортирован `t` и `$page`
- Заменены переводы:
  - ✅ Label: "Language:"
  - ✅ Option: "All Languages"

---

### 6. Обновлен +layout.svelte
**Файл:** `packages/frontend/src/routes/+layout.svelte`

**Изменения:**
- Импортирован `t` и `$page`
- Получает переводы из `$page.data.translations`
- ✅ Offline banner text теперь переводной

---

## 📊 Статистика

**Созданные файлы:**
- `src/lib/utils/i18n.ts` (230 строк)
- `src/routes/+layout.gql` (7 строк)
- `src/routes/+layout.ts` (30 строк)

**Обновленные файлы:**
- `src/lib/utils/index.ts`
- `src/lib/components/AppHeader.svelte`
- `src/lib/components/LanguageSwitcher.svelte`
- `src/routes/+layout.svelte`

**Переведенные элементы UI:**
- Navigation: 4 ссылки
- Buttons: 3 кнопки
- Labels: 2 элемента
- Messages: 1 offline banner

---

## 🧪 Как протестировать

### Вариант 1: Запуск в Docker

```bash
# Убедитесь что backend запущен с UI seed data
cd packages/frontend

# Установить зависимости (если еще не установлено)
npm install

# Сгенерировать Houdini types
npm run generate

# Запустить dev сервер
npm run dev
```

### Вариант 2: Полный запуск через Docker Compose

```bash
# Запустить весь стек
docker-compose up -d

# Проверить логи
docker-compose logs frontend
docker-compose logs backend
```

---

## ✅ Проверка результатов

### 1. Открыть приложение
Откройте: http://localhost:5173

### 2. Проверить Header
- [ ] Navigation links отображаются на английском (по умолчанию)
- [ ] Кнопки "Sign in" и "Get Started" видны

### 3. Переключить язык
- [ ] Выбрать **Russian (ru)** в Language Switcher
- [ ] Navigation должен измениться:
  - "Dashboard" → "Панель управления"
  - "Concepts" → "Концепции"
  - "Languages" → "Языки"
  - "Dictionaries" → "Словари"
- [ ] Кнопки должны измениться:
  - "Sign in" → "Войти"
  - "Get Started" → "Начать"
- [ ] Label "Language:" → "Язык:"

### 4. Проверить Spanish (es)
- [ ] Выбрать **Español (es)**
- [ ] Navigation:
  - "Dashboard" → "Panel de control"
  - "Concepts" → "Conceptos"
  - etc.

### 5. Проверить Fallback
- [ ] Если перевод не найден, должен показываться ключ или fallback
- [ ] Например: `ui/nav/admin` → показывается "admin" или fallback текст

---

## 🐛 Возможные проблемы

### Проблема: "Cannot read property 'translations' of undefined"
**Решение:**
```typescript
// В компоненте добавьте проверку
const trans = $derived($page.data?.translations || {});
```

### Проблема: "GetUITranslationsStore is not defined"
**Решение:**
```bash
# Сгенерировать Houdini types
cd packages/frontend
npm run generate
```

### Проблема: Переводы не загружаются
**Решение:**
1. Проверить что backend запущен: http://localhost:8000/graphql
2. Проверить что UI seed data применился (см. PHASE1_COMPLETED.md)
3. Проверить query в GraphQL Playground:
```graphql
query GetUITranslations {
  dictionaries(languageId: 2, limit: 300) {
    concept {
      path
    }
    name
  }
}
```

### Проблема: Переводы не меняются при переключении языка
**Решение:**
- В текущей реализации требуется перезагрузка страницы
- Это будет исправлено в Phase 4 (реактивное переключение)

---

## 📝 Примеры использования

### В компоненте

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { t } from '$lib/utils/i18n';

  const trans = $derived($page.data.translations || {});
</script>

<h1>{t(trans, 'ui/home/title', 'Home')}</h1>
<button>{t(trans, 'ui/button/save', 'Save')}</button>
```

### С параметрами (будущая функциональность)

```svelte
<script lang="ts">
  import { tParams } from '$lib/utils/i18n';

  const greeting = tParams(trans, 'ui/greeting', { name: 'John' });
  // "Hello, John!" или "Привет, John!"
</script>
```

### С namespace

```svelte
<script lang="ts">
  import { createNamespaceT } from '$lib/utils/i18n';

  // Создать функцию для конкретного namespace
  const navT = createNamespaceT(trans, 'ui/nav');

  // Использовать без префикса
  const dashboardText = navT('dashboard'); // автоматически = ui/nav/dashboard
</script>
```

---

## 🎯 Следующие шаги (Phase 3)

### Обновить страницы для использования переводов:

1. **Home Page** (`/`)
   - Hero section: title, subtitle, description
   - Features: 3 карточки с заголовками и описаниями
   - CTA section
   - Footer

2. **Dashboard** (`/dashboard`)
   - Page title, welcome message
   - Stats cards

3. **Concepts** (`/concepts`)
   - Page title, search placeholder
   - Table headers, button labels

4. **Languages** (`/languages`)
   - Page title, table headers

5. **Dictionaries** (`/dictionaries`)
   - Page title, search placeholder

6. **Auth Pages** (`/login`, `/register`, `/forgot-password`)
   - Page titles, form labels, button texts

**Для каждой страницы:**
- Создать `+page.ts` с load function (если нет)
- Загрузить переводы для соответствующего path
- Заменить hardcoded тексты на `t()`

---

## 📋 Checklist для Phase 2

- [x] Создать i18n utility функции
- [x] Создать GraphQL query для UI-переводов
- [x] Создать +layout.ts с load function
- [x] Обновить AppHeader.svelte
- [x] Обновить LanguageSwitcher.svelte
- [x] Обновить +layout.svelte (offline banner)
- [ ] Протестировать переключение языков
- [ ] Проверить все переводы загружаются
- [ ] Проверить fallback работает

---

## 📚 Дополнительные ресурсы

**Созданные переводы (из Phase 1):**
- Navigation: `ui/nav/*`
- Buttons: `ui/button/*`
- Labels: `ui/label/*`
- Common: `ui/common/*`

**См. полный список:** `packages/backend/scripts/seed_ui_concepts.py`

**Houdini документация:**
- https://houdinigraphql.com/
- Load functions: https://houdinigraphql.com/guides/loading-data

**SvelteKit документация:**
- Load functions: https://kit.svelte.dev/docs/load

---

**Дата:** 2025-10-23
**Статус:** ✅ Phase 2 Complete - Header & Navigation Translated
**Следующий шаг:** Phase 3 - Update remaining pages
