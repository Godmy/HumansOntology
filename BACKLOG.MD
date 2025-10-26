# Backlog - HumansOntology: Multilingual UI System

**Цель проекта:** Реализовать полную систему многоязычности для веб-интерфейса, где весь текст будет храниться в базе данных и динамически загружаться в зависимости от выбранного языка.

---

## Легенда приоритетов

- 🔥 **P0** - Критический (необходимо для базовой функциональности)
- ⚡ **P1** - Высокий приоритет (важно для пользователей)
- 📌 **P2** - Средний приоритет (улучшение UX)
- 💡 **P3** - Низкий приоритет (nice to have)

## Статусы

- 📋 **Backlog** - в очереди
- 🚧 **In Progress** - в разработке
- ✅ **Done** - завершено
- 🔒 **Blocked** - заблокировано

---

## Текущее состояние проекта

### ✅ Уже реализовано:

**Backend:**
- Модель `Language` для хранения языков (код, название)
- Модель `Dictionary` для переводов концепций (concept_id, language_id, name, description)
- GraphQL API для управления языками и концепциями
- Seed data с 8 языками (en, ru, fr, de, es, it, ja, zh)

**Frontend:**
- `LanguageStore` для управления текущим выбранным языком
- `LanguageSwitcher` компонент для переключения языков
- Интеграция с localStorage для сохранения выбора
- Базовая структура приложения (SvelteKit + Houdini GraphQL)

### ❌ Требуется реализовать:

**Backend:**
- Модель для хранения UI-переводов (меню, кнопки, заголовки страниц)
- GraphQL API для получения UI-переводов
- Seed data для базовых UI-переводов всех страниц
- Система fallback для отсутствующих переводов

**Frontend:**
- i18n Store/Service для загрузки и кэширования переводов
- Утилита `t()` (translate) для использования в компонентах
- Интеграция с `languageStore` для автоматического переключения
- Обновление всех страниц и компонентов для использования переводов
- Loading state во время загрузки переводов
- Система fallback на английский язык

---

## 🔥 Phase 1: Backend - Database Schema & API (P0)

### #1 - Создание модели UITranslation для хранения UI-переводов

**User Story:**
Как backend-разработчик, я хочу модель для хранения переводов UI-элементов, чтобы весь текст интерфейса можно было управлять через БД.

**Acceptance Criteria:**
- [ ] Создать модель `UITranslationModel` в `packages/backend/languages/models/ui_translation.py`
  - `key: String(255)` - уникальный ключ перевода (например, `nav.dashboard`, `button.save`)
  - `routes: String(255)` - страница/раздел который известен в Svelte-Kit (например, `header`, `dashboard`, `concepts`)
  - `language_id: ForeignKey(Language)` - связь с языком
  - `value: Text` - переведенный текст
  - Уникальный индекс на пару `(key, language_id)`
- [ ] Добавить relationship к `LanguageModel`
- [ ] Реализовать soft delete через `SoftDeleteMixin`
- [ ] Добавить `__repr__` метод для удобной отладки

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Файлы для создания:**
- `packages/backend/languages/models/ui_translation.py`

**Пример структуры:**
```python
class UITranslationModel(SoftDeleteMixin, BaseModel):
    __tablename__ = "ui_translations"

    key = Column(String(255), nullable=False, index=True)
    page = Column(String(100), nullable=False, index=True)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    value = Column(Text, nullable=False)
    context = Column(String(500))

    language = relationship("LanguageModel", back_populates="ui_translations")
```

---

### #2 - Создание Alembic миграции для UITranslation

**User Story:**
Как DevOps инженер, я хочу миграцию для создания таблицы UI-переводов, чтобы применить изменения в БД.

**Acceptance Criteria:**
- [ ] Создать миграцию через `alembic revision --autogenerate -m "Add ui_translations table"`
- [ ] Проверить корректность миграции (up/down)
- [ ] Добавить уникальный индекс на `(key, language_id)`
- [ ] Добавить индексы на `key`, `page`, `language_id`
- [ ] Протестировать применение и откат миграции

**Estimated Effort:** 2 story points

**Status:** 📋 Backlog

**Зависимости:** #1

---

### #3 - Создание GraphQL schemas для UI-переводов

**User Story:**
Как frontend-разработчик, я хочу GraphQL API для получения UI-переводов, чтобы динамически загружать тексты интерфейса.

**Acceptance Criteria:**
- [ ] Создать Strawberry types в `packages/backend/languages/schemas/ui_translation.py`:
  - `UITranslationType` (id, key, page, language_id, value, context)
  - `UITranslationInput` (key, page, language_id, value, context)
- [ ] Добавить queries:
  - `uiTranslations(languageId: Int!, page: String): [UITranslationType]` - получить все переводы для языка и опционально страницы
  - `uiTranslation(key: String!, languageId: Int!): UITranslationType` - получить конкретный перевод
  - `uiTranslationsByPage(page: String!, languageId: Int!): [UITranslationType]` - получить переводы для страницы
- [ ] Добавить mutations (для админов):
  - `createUITranslation(input: UITranslationInput!): UITranslationType`
  - `updateUITranslation(id: Int!, input: UITranslationInput!): UITranslationType`
  - `deleteUITranslation(id: Int!): Boolean`
  - `bulkCreateUITranslations(translations: [UITranslationInput!]!): [UITranslationType]`
- [ ] Добавить permission checks для mutations (`admin:update`)
- [ ] Интегрировать в `core/schemas/schema.py`

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #1, #2

**Пример GraphQL запроса:**
```graphql
query GetUITranslations($languageId: Int!, $page: String) {
  uiTranslations(languageId: $languageId, page: $page) {
    key
    value
  }
}
```

---

### #4 - Создание service для UITranslation

**User Story:**
Как backend-разработчик, я хочу сервис с бизнес-логикой для UI-переводов, чтобы централизовать операции с переводами.

**Acceptance Criteria:**
- [ ] Создать `UITranslationService` в `packages/backend/languages/services/ui_translation_service.py`
- [ ] Реализовать методы:
  - `get_translations(language_id: int, page: Optional[str]) -> List[UITranslationModel]`
  - `get_translation(key: str, language_id: int) -> Optional[UITranslationModel]`
  - `get_translations_by_page(page: str, language_id: int) -> List[UITranslationModel]`
  - `create_translation(data: dict) -> UITranslationModel`
  - `update_translation(id: int, data: dict) -> UITranslationModel`
  - `delete_translation(id: int) -> bool`
  - `bulk_create_translations(translations: List[dict]) -> List[UITranslationModel]`
  - `get_all_pages() -> List[str]` - получить список всех страниц с переводами
- [ ] Добавить валидацию входных данных
- [ ] Реализовать fallback на английский язык если перевод не найден
- [ ] Добавить кэширование через Redis (опционально)

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #1, #2

---

### #5 - Создание seed data для UI-переводов

**User Story:**
Как разработчик, я хочу базовые UI-переводы при инициализации БД, чтобы приложение работало из коробки.

**Acceptance Criteria:**
- [ ] Создать функцию `seed_ui_translations()` в `packages/backend/scripts/seed_data.py`
- [ ] Подготовить переводы для всех существующих страниц:
  - **Header/Navigation:** `nav.dashboard`, `nav.concepts`, `nav.languages`, `nav.dictionaries`, `nav.admin`, `button.login`, `button.logout`, `button.register`, `button.getStarted`, `text.signIn`, `label.language`
  - **Home Page:** `home.title`, `home.subtitle`, `home.description`, `home.cta.title`, `home.cta.description`, `home.features.concepts.title`, `home.features.concepts.description`, `home.features.multilang.title`, `home.features.multilang.description`, `home.features.roles.title`, `home.features.roles.description`
  - **Dashboard:** `dashboard.title`, `dashboard.welcome`, `dashboard.stats.users`, `dashboard.stats.concepts`, `dashboard.stats.languages`
  - **Concepts:** `concepts.title`, `concepts.create`, `concepts.edit`, `concepts.delete`, `concepts.search`, `concepts.filter`, `concepts.table.name`, `concepts.table.language`, `concepts.table.actions`
  - **Languages:** `languages.title`, `languages.create`, `languages.edit`, `languages.table.code`, `languages.table.name`
  - **Dictionaries:** `dictionaries.title`, `dictionaries.search`, `dictionaries.filter`
  - **Common:** `common.save`, `common.cancel`, `common.delete`, `common.edit`, `common.create`, `common.search`, `common.filter`, `common.loading`, `common.error`, `common.success`, `common.noData`, `common.back`
  - **Auth:** `auth.login.title`, `auth.register.title`, `auth.forgotPassword.title`, `auth.email`, `auth.password`, `auth.username`
- [ ] Создать переводы для минимум 3 языков: English (en), Russian (ru), Spanish (es)
- [ ] Интегрировать вызов в `init_db.py`
- [ ] Добавить проверку на существование переводов (не дублировать)

**Estimated Effort:** 8 story points

**Status:** 📋 Backlog

**Зависимости:** #1, #2, #4

**Структура данных:**
```python
UI_TRANSLATIONS = {
    'en': {
        'header': {
            'nav.dashboard': 'Dashboard',
            'nav.concepts': 'Concepts',
            'button.logout': 'Logout',
            ...
        },
        'home': {
            'home.title': 'Multilingual Content',
            'home.subtitle': 'Management',
            ...
        }
    },
    'ru': {
        'header': {
            'nav.dashboard': 'Панель управления',
            'nav.concepts': 'Концепции',
            'button.logout': 'Выйти',
            ...
        },
        ...
    }
}
```

---

### #6 - Создание GraphQL query для bulk загрузки переводов

**User Story:**
Как frontend-разработчик, я хочу эффективный способ загрузки всех переводов одним запросом, чтобы минимизировать количество API вызовов.

**Acceptance Criteria:**
- [ ] Добавить query `getAllUITranslations(languageId: Int!): [UITranslationType]`
- [ ] Реализовать группировку результатов по `page` на backend
- [ ] Добавить кэширование результата на 1 час (Redis)
- [ ] Оптимизировать запрос (использовать joinedload)
- [ ] Добавить pagination (опционально, limit/offset)

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #3, #4

---

## ⚡ Phase 2: Frontend - i18n System (P0)

### #7 - Создание i18nStore для управления переводами

**User Story:**
Как frontend-разработчик, я хочу store для управления UI-переводами, чтобы легко получать переводы в компонентах.

**Acceptance Criteria:**
- [ ] Создать `i18nStore.svelte.ts` в `packages/frontend/src/lib/stores/`
- [ ] Реализовать функционал:
  - `translations: Record<string, string>` - словарь переводов (key -> value)
  - `isLoading: boolean` - состояние загрузки
  - `currentLanguageId: number | null` - текущий язык (синхронизация с `languageStore`)
  - `loadTranslations(languageId: number): Promise<void>` - загрузить переводы для языка
  - `t(key: string, fallback?: string): string` - получить перевод по ключу
  - `getTranslationsByPage(page: string): Record<string, string>` - получить переводы для страницы
- [ ] Добавить кэширование переводов в памяти (Map<languageId, translations>)
- [ ] Реализовать fallback на ключ, если перевод не найден
- [ ] Интегрировать с `languageStore` для автоматического переключения
- [ ] Использовать Svelte 5 Runes ($state, $derived, $effect)

**Estimated Effort:** 8 story points

**Status:** 📋 Backlog

**Зависимости:** #6

**Пример использования:**
```typescript
import { i18nStore } from '$lib/stores/i18nStore.svelte';

// В компоненте
const t = i18nStore.t;
console.log(t('nav.dashboard')); // "Dashboard" или "Панель управления"
```

---

### #8 - Создание Houdini query для загрузки UI-переводов

**User Story:**
Как frontend-разработчик, я хочу GraphQL запрос для загрузки переводов, чтобы интегрировать с i18nStore.

**Acceptance Criteria:**
- [ ] Создать query в `packages/frontend/src/lib/api/queries/uiTranslations.gql`:
  ```graphql
  query GetUITranslations($languageId: Int!) {
    uiTranslations(languageId: $languageId) {
      key
      value
    }
  }
  ```
- [ ] Настроить Houdini для генерации типов
- [ ] Добавить error handling
- [ ] Добавить retry логику (опционально)

**Estimated Effort:** 2 story points

**Status:** 📋 Backlog

**Зависимости:** #7

---

### #9 - Создание утилиты t() для использования в компонентах

**User Story:**
Как frontend-разработчик, я хочу удобную функцию `t()` для использования переводов в компонентах, чтобы код был читаемым.

**Acceptance Criteria:**
- [ ] Создать `i18n.ts` utility в `packages/frontend/src/lib/utils/`
- [ ] Реализовать:
  - `t(key: string, fallback?: string): string` - получить перевод
  - `tPage(page: string, key: string, fallback?: string): string` - получить перевод для конкретной страницы
  - Reactive переключение при смене языка
- [ ] Добавить TypeScript типы для ключей (опционально)
- [ ] Поддержать интерполяцию параметров (опционально, для `Hello, {name}`)
- [ ] Добавить unit tests

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #7

---

### #10 - Интеграция i18nStore с layout для автозагрузки переводов

**User Story:**
Как пользователь, я хочу чтобы переводы загружались автоматически при загрузке приложения, чтобы видеть интерфейс на своем языке.

**Acceptance Criteria:**
- [ ] Обновить `+layout.svelte` для загрузки переводов в `onMount`
- [ ] Добавить реактивность на изменение `languageStore.currentLanguageId`
- [ ] Реализовать $effect для автоматической перезагрузки при смене языка
- [ ] Добавить loading state (показывать spinner во время загрузки)
- [ ] Реализовать fallback на английский (en) при ошибке загрузки
- [ ] Показывать toast notification при ошибке загрузки

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #7, #8

**Пример кода:**
```svelte
<script>
import { i18nStore } from '$lib/stores/i18nStore.svelte';
import { languageStore } from '$lib/stores/languageStore.svelte';
import { onMount } from 'svelte';

onMount(async () => {
  // Load translations for current language
  const langId = languageStore.currentLanguageId || 1; // fallback to English
  await i18nStore.loadTranslations(langId);
});

// Auto-reload translations when language changes
$effect(() => {
  const langId = languageStore.currentLanguageId;
  if (langId) {
    i18nStore.loadTranslations(langId);
  }
});
</script>
```

---

## ⚡ Phase 3: Frontend - UI Integration (P1)

### #11 - Обновление AppHeader для использования переводов

**User Story:**
Как пользователь, я хочу видеть меню навигации на выбранном языке, чтобы лучше понимать интерфейс.

**Acceptance Criteria:**
- [ ] Заменить hardcoded тексты на вызовы `t()`:
  - Navigation links: `Dashboard`, `Concepts`, `Languages`, `Dictionaries`
  - Buttons: `Sign in`, `Get Started`, `Logout`
  - Label: `Language:`
- [ ] Добавить fallback для каждого текста
- [ ] Проверить реактивное переключение при смене языка
- [ ] Протестировать с 3+ языками

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

**До:**
```svelte
<a href="/dashboard">Dashboard</a>
```

**После:**
```svelte
<a href="/dashboard">{t('nav.dashboard', 'Dashboard')}</a>
```

---

### #12 - Обновление Home Page (+page.svelte) для использования переводов

**User Story:**
Как посетитель сайта, я хочу видеть главную страницу на моем языке, чтобы лучше понять продукт.

**Acceptance Criteria:**
- [ ] Заменить все тексты на вызовы `t()`:
  - Hero section: title, subtitle, description
  - Features: titles, descriptions
  - CTA sections
  - Footer
- [ ] Сохранить существующий дизайн и верстку
- [ ] Добавить fallback для всех текстов
- [ ] Протестировать responsive дизайн

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

### #13 - Обновление Dashboard Page для использования переводов

**User Story:**
Как пользователь, я хочу видеть панель управления на моем языке.

**Acceptance Criteria:**
- [ ] Заменить все тексты на `t()`:
  - Page title, welcome message
  - Stats cards titles
  - Button labels
- [ ] Добавить fallback
- [ ] Протестировать с разными языками

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

### #14 - Обновление Concepts Page для использования переводов

**User Story:**
Как пользователь, я хочу видеть страницу концепций на моем языке.

**Acceptance Criteria:**
- [ ] Заменить все тексты на `t()`:
  - Page title
  - Search placeholder
  - Table headers (Name, Language, Actions)
  - Button labels (Create, Edit, Delete)
  - Filter labels
  - Empty state messages
- [ ] Добавить fallback
- [ ] Протестировать CRUD операции

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

### #15 - Обновление Languages Page для использования переводов

**User Story:**
Как пользователь, я хочу видеть страницу языков на моем языке.

**Acceptance Criteria:**
- [ ] Заменить все тексты на `t()`:
  - Page title
  - Table headers (Code, Name)
  - Button labels
  - Form labels
- [ ] Добавить fallback
- [ ] Протестировать CRUD операции

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

### #16 - Обновление Dictionaries Page для использования переводов

**User Story:**
Как пользователь, я хочу видеть страницу словарей на моем языке.

**Acceptance Criteria:**
- [ ] Заменить все тексты на `t()`:
  - Page title
  - Search/filter labels
  - Table headers
  - Button labels
- [ ] Добавить fallback
- [ ] Протестировать поиск и фильтрацию

**Estimated Effort:** 3 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

### #17 - Обновление Auth Pages (Login, Register, Forgot Password)

**User Story:**
Как пользователь, я хочу видеть страницы авторизации на моем языке.

**Acceptance Criteria:**
- [ ] Обновить Login page:
  - Title, form labels, button texts, error messages
- [ ] Обновить Register page:
  - Title, form labels, button texts, validation messages
- [ ] Обновить Forgot Password page:
  - Title, form labels, button texts
- [ ] Добавить fallback для всех текстов
- [ ] Протестировать flow авторизации

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #9, #10

---

## 📌 Phase 4: Enhancement & Optimization (P2)

### #18 - Добавление Redis кэширования для UI-переводов (Backend)

**User Story:**
Как DevOps инженер, я хочу кэшировать UI-переводы в Redis, чтобы снизить нагрузку на БД.

**Acceptance Criteria:**
- [ ] Добавить кэширование в `UITranslationService`:
  - Cache key: `ui_translations:{language_id}`
  - TTL: 1 hour
- [ ] Реализовать cache invalidation при обновлении переводов
- [ ] Добавить fallback на БД при недоступности Redis
- [ ] Добавить метрики для cache hit/miss rate

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #4

---

### #19 - Добавление localStorage кэширования для переводов (Frontend)

**User Story:**
Как frontend-разработчик, я хочу кэшировать переводы в localStorage, чтобы ускорить загрузку при повторных визитах.

**Acceptance Criteria:**
- [ ] Сохранять переводы в localStorage:
  - Key: `multipult_translations_{languageId}`
  - Version control (invalidate при обновлении версии)
- [ ] Загружать из cache при инициализации
- [ ] Обновлять в фоне для актуальности
- [ ] Реализовать TTL для cache (24 часа)
- [ ] Добавить admin опцию "Clear translations cache"

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #7

---

### #20 - Создание Admin UI для управления переводами

**User Story:**
Как администратор, я хочу веб-интерфейс для управления UI-переводами, чтобы не работать напрямую с БД.

**Acceptance Criteria:**
- [ ] Создать страницу `/admin/translations`
- [ ] Реализовать таблицу с переводами:
  - Columns: Key, Page, Language, Value, Actions
  - Фильтры: по языку, по странице
  - Поиск по ключу/значению
- [ ] Добавить формы:
  - Create translation
  - Edit translation (inline editing)
  - Bulk import (JSON/CSV)
  - Bulk export (JSON/CSV)
- [ ] Добавить валидацию:
  - Проверка на дубликаты ключей
  - Обязательные поля
- [ ] Добавить permission check (только admin)
- [ ] Реализовать preview переводов

**Estimated Effort:** 13 story points

**Status:** 📋 Backlog

**Зависимости:** #3, #4

---

### #21 - Реализация интерполяции параметров в переводах

**User Story:**
Как разработчик, я хочу поддержку параметров в переводах (`Hello, {name}!`), чтобы создавать динамические сообщения.

**Acceptance Criteria:**
- [ ] Обновить функцию `t()` для поддержки параметров:
  - Синтаксис: `t('greeting.hello', { name: 'John' })`
  - Результат: "Hello, John!" или "Привет, John!"
- [ ] Поддержать множественные параметры
- [ ] Реализовать escape для безопасности
- [ ] Добавить примеры в seed data
- [ ] Обновить TypeScript типы

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #9

---

### #22 - Поддержка плюрализации (plural forms)

**User Story:**
Как разработчик, я хочу поддержку множественных форм (`1 item`, `2 items`), чтобы корректно отображать числа.

**Acceptance Criteria:**
- [ ] Добавить функцию `tn()` (translate number):
  - Пример: `tn('items.count', count, { count })`
  - English: "1 item" / "2 items"
  - Russian: "1 предмет" / "2 предмета" / "5 предметов"
- [ ] Реализовать plural rules для разных языков
- [ ] Добавить примеры в seed data
- [ ] Обновить документацию

**Estimated Effort:** 8 story points

**Status:** 📋 Backlog

**Зависимости:** #21

---

### #23 - Создание CLI tool для экспорта/импорта переводов

**User Story:**
Как администратор, я хочу CLI tool для работы с переводами, чтобы автоматизировать рабочие процессы.

**Acceptance Criteria:**
- [ ] Создать CLI команды в `packages/backend/scripts/translations_cli.py`:
  - `export-translations --language <code> --output <file.json>` - экспорт
  - `import-translations --input <file.json>` - импорт
  - `validate-translations` - проверка на отсутствующие ключи
  - `list-missing-keys --language <code>` - показать недостающие переводы
- [ ] Поддержать форматы: JSON, CSV, XLSX
- [ ] Добавить dry-run mode
- [ ] Добавить progress bar для bulk операций
- [ ] Интегрировать в Docker как команду

**Estimated Effort:** 8 story points

**Status:** 📋 Backlog

**Зависимости:** #4

---

## 💡 Phase 5: Advanced Features (P3)

### #24 - Интеграция с профессиональными CAT tools (Translation Memory)

**User Story:**
Как переводчик, я хочу интегрировать систему с CAT tools (Trados, MemoQ), чтобы использовать профессиональные инструменты перевода.

**Acceptance Criteria:**
- [ ] Экспорт в TMX (Translation Memory eXchange) format
- [ ] Импорт из TMX
- [ ] Поддержка XLIFF format
- [ ] Интеграция с translation APIs (Google Translate, DeepL) для автоматических предложений
- [ ] Translation memory для повторяющихся фраз

**Estimated Effort:** 13 story points

**Status:** 📋 Backlog

**Зависимости:** #23

---

### #25 - Система версионирования переводов

**User Story:**
Как переводчик, я хочу видеть историю изменений переводов, чтобы откатиться к предыдущим версиям.

**Acceptance Criteria:**
- [ ] Добавить модель `UITranslationVersion`:
  - translation_id, version, value, changed_by, changed_at
- [ ] Автоматическое создание версий при обновлении
- [ ] UI для просмотра истории изменений
- [ ] Возможность rollback к предыдущей версии
- [ ] Diff view между версиями

**Estimated Effort:** 13 story points

**Status:** 📋 Backlog

**Зависимости:** #4

---

### #26 - Система review/approval для переводов

**User Story:**
Как менеджер переводов, я хочу систему утверждения переводов, чтобы контролировать качество.

**Acceptance Criteria:**
- [ ] Добавить статусы для переводов: `draft`, `pending_review`, `approved`, `rejected`
- [ ] Реализовать workflow:
  - Переводчик создает/обновляет перевод → `draft`
  - Отправляет на review → `pending_review`
  - Reviewer утверждает/отклоняет → `approved`/`rejected`
- [ ] Добавить комментарии к переводам
- [ ] UI для review queue
- [ ] Email notifications для reviewers
- [ ] Permission system: translator, reviewer, admin

**Estimated Effort:** 21 story points

**Status:** 📋 Backlog

**Зависимости:** #20

---

### #27 - A/B тестирование переводов

**User Story:**
Как product manager, я хочу тестировать разные варианты переводов, чтобы выбрать наиболее эффективный.

**Acceptance Criteria:**
- [ ] Поддержка вариантов переводов (A/B/C)
- [ ] Автоматическое распределение пользователей по вариантам
- [ ] Метрики для каждого варианта (CTR, conversion)
- [ ] UI для создания и управления экспериментами
- [ ] Автоматическое определение winner

**Estimated Effort:** 21 story points

**Status:** 📋 Backlog

**Зависимости:** #20

---

### #28 - Автоматическое определение языка по user locale

**User Story:**
Как пользователь, я хочу чтобы система автоматически определяла мой язык, чтобы не выбирать его вручную.

**Acceptance Criteria:**
- [ ] Определять язык из `Accept-Language` header
- [ ] Определять из browser locale (navigator.language)
- [ ] Fallback на английский если язык не поддерживается
- [ ] Сохранять выбор в localStorage
- [ ] Пользователь может переопределить автоматический выбор

**Estimated Effort:** 5 story points

**Status:** 📋 Backlog

**Зависимости:** #7

---

### #29 - Поддержка RTL (Right-to-Left) языков

**User Story:**
Как пользователь арабского/иврита, я хочу корректное отображение RTL текста, чтобы удобно пользоваться системой.

**Acceptance Criteria:**
- [ ] Добавить поле `direction` в модель Language (`ltr`/`rtl`)
- [ ] Автоматически переключать CSS direction при смене языка
- [ ] Обновить компоненты для поддержки RTL:
  - Navigation alignment
  - Text alignment
  - Icon positions
- [ ] Протестировать с арабским языком (ar)
- [ ] Добавить seed data для арабского языка

**Estimated Effort:** 13 story points

**Status:** 📋 Backlog

**Зависимости:** #7, #11-17

---

### #30 - Offline support для переводов (PWA)

**User Story:**
Как пользователь, я хочу работать с приложением offline, чтобы не зависеть от интернета.

**Acceptance Criteria:**
- [ ] Сохранять переводы в IndexedDB
- [ ] Service Worker для кэширования
- [ ] Sync переводов при восстановлении соединения
- [ ] Показывать offline indicator
- [ ] Graceful degradation при отсутствии соединения

**Estimated Effort:** 13 story points

**Status:** 📋 Backlog

**Зависимости:** #19

---

## 📊 Summary

### By Priority
- **P0 (Critical):** 17 tasks, ~78 story points
  - Phase 1 (Backend): 6 tasks, 26 SP
  - Phase 2 (Frontend i18n): 4 tasks, 18 SP
  - Phase 3 (UI Integration): 7 tasks, 27 SP
- **P1 (High):** 0 tasks
- **P2 (Medium):** 6 tasks, ~49 story points
- **P3 (Nice to Have):** 7 tasks, ~99 story points

### Total
- **30 tasks**
- **~226 story points**

---

## Рекомендуемая последовательность выполнения

### Week 1-2: Backend Foundation
1. #1 → #2 → #4 → #3 (модель, миграция, сервис, schemas)
2. #5 (seed data)
3. #6 (bulk query)

### Week 3-4: Frontend i18n System
1. #8 → #7 (query → store)
2. #9 (utility function)
3. #10 (layout integration)

### Week 5-6: UI Integration
1. #11 (Header)
2. #12 (Home Page)
3. #13 → #14 → #15 → #16 (Dashboard + main pages)
4. #17 (Auth pages)

### Week 7+: Enhancements (optional)
1. #18 → #19 (caching)
2. #20 (admin UI)
3. #21 → #22 (interpolation + pluralization)
4. #23 (CLI tools)

---

## Testing Checklist

После завершения основных фаз (P0) необходимо протестировать:

- [ ] **Backend Tests:**
  - [ ] Unit tests для UITranslationService
  - [ ] Integration tests для GraphQL API
  - [ ] Миграции (up/down)
  - [ ] Seed data применяется корректно

- [ ] **Frontend Tests:**
  - [ ] Unit tests для i18nStore
  - [ ] Unit tests для функции t()
  - [ ] Интеграционные тесты для переключения языков
  - [ ] E2E tests для основных страниц

- [ ] **Manual Testing:**
  - [ ] Переключение между 3+ языками
  - [ ] Все страницы отображают переводы корректно
  - [ ] Fallback работает при отсутствии перевода
  - [ ] localStorage сохраняет выбор языка
  - [ ] Нет hardcoded текстов

- [ ] **Performance:**
  - [ ] Время загрузки переводов < 500ms
  - [ ] Нет N+1 queries
  - [ ] Кэширование работает эффективно

- [ ] **UX:**
  - [ ] Smooth переключение языков без перезагрузки
  - [ ] Loading states показываются корректно
  - [ ] Ошибки обрабатываются gracefully

---

## Notes

- Все задачи можно выполнять параллельно в рамках одной фазы
- Backend (Phase 1) должен быть завершен перед началом Frontend (Phase 2)
- Phase 3 можно начинать сразу после завершения Phase 2
- Phase 4-5 опциональны и могут выполняться по необходимости

**Контактная информация для вопросов:** См. README.md основного проекта
