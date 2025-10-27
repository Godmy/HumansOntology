# Backlog - HumansOntology: Multilingual UI (Simplified Approach)

**Цель:** Весь текст интерфейса берется из базы данных используя **существующую модель Dictionary**.

**Ключевая идея:** Создаем специальные концепты для UI-элементов (например, `ui.nav.dashboard`) и их переводы храним в Dictionary. SvelteKit через Houdini получает данные и компоненты просто используют их.

---

## Архитектура (How It Works)

```
User выбирает язык → languageStore.setLanguage(languageId)
                              ↓
         SvelteKit route load function (+page.ts)
                              ↓
         Houdini GraphQL query к Strawberry
         getDictionaries(languageId, conceptPath: "/ui/...")
                              ↓
         Возвращает: [{ concept.name: "ui.nav.dashboard", name: "Dashboard" }, ...]
                              ↓
         Компоненты: <h1>{translations['ui.nav.dashboard']}</h1>
```

### Преимущества подхода:
✅ Используем существующую модель `Dictionary` - **никаких новых таблиц**
✅ GraphQL API уже работает - минимальные изменения
✅ SvelteKit load functions - естественная интеграция
✅ Простая поддержка - один источник правды (БД)

---

## 🔥 Implementation Plan

### Phase 1: Backend (1 week)

#### #1 - Создать UI-концепты в seed data

**Что делать:**
- [ ] Создать скрипт `packages/backend/scripts/seed_ui_concepts.py`
- [ ] Создать концепты для UI элементов с путями типа `/ui/nav/dashboard`
- [ ] Для каждого концепта создать Dictionary записи для EN, RU, ES
- [ ] Интегрировать в `init_db.py`

**Структура данных:**
```python
UI_CONCEPTS = {
    'ui.nav.dashboard': {
        'path': '/ui/nav/dashboard',
        'en': 'Dashboard',
        'ru': 'Панель управления',
        'es': 'Panel de control'
    },
    'ui.nav.concepts': {
        'path': '/ui/nav/concepts',
        'en': 'Concepts',
        'ru': 'Концепции',
        'es': 'Conceptos'
    },
    'ui.button.login': {
        'path': '/ui/button/login',
        'en': 'Login',
        'ru': 'Войти',
        'es': 'Iniciar sesión'
    },
    # ... ~50 ключей для всех страниц
}
```

**Ключи для создания:**

**Navigation (Header):**
- `ui.nav.dashboard`, `ui.nav.concepts`, `ui.nav.languages`, `ui.nav.dictionaries`, `ui.nav.admin`
- `ui.button.login`, `ui.button.logout`, `ui.button.register`, `ui.button.getStarted`, `ui.button.signIn`
- `ui.label.language`

**Home Page:**
- `ui.home.title`, `ui.home.subtitle`, `ui.home.description`
- `ui.home.cta.title`, `ui.home.cta.description`, `ui.home.cta.button`
- `ui.home.feature.concepts.title`, `ui.home.feature.concepts.desc`
- `ui.home.feature.multilang.title`, `ui.home.feature.multilang.desc`
- `ui.home.feature.roles.title`, `ui.home.feature.roles.desc`
- `ui.home.footer.copyright`

**Dashboard:**
- `ui.dashboard.title`, `ui.dashboard.welcome`
- `ui.dashboard.stats.users`, `ui.dashboard.stats.concepts`, `ui.dashboard.stats.languages`

**Concepts:**
- `ui.concepts.title`, `ui.concepts.create`, `ui.concepts.edit`, `ui.concepts.delete`
- `ui.concepts.search`, `ui.concepts.filter`
- `ui.concepts.table.name`, `ui.concepts.table.language`, `ui.concepts.table.actions`

**Common:**
- `ui.common.save`, `ui.common.cancel`, `ui.common.delete`, `ui.common.edit`, `ui.common.create`
- `ui.common.search`, `ui.common.filter`, `ui.common.loading`, `ui.common.error`, `ui.common.success`

**Effort:** 1 day

---

#### #2 - Добавить GraphQL query filter для UI-переводов (optional)

**Что делать:**
- [ ] Добавить фильтр `conceptPathPrefix` в existing `dictionaries` query
- [ ] Позволит загружать все переводы страницы одним запросом
- [ ] Пример: `dictionaries(languageId: 1, conceptPathPrefix: "/ui/nav")` → вернет все navigation переводы

**Изменения в `packages/backend/languages/services/dictionary_service.py`:**
```python
def get_dictionaries(
    self,
    language_id: Optional[int] = None,
    concept_path_prefix: Optional[str] = None,  # NEW
    limit: int = 100,
    offset: int = 0
) -> List[DictionaryModel]:
    query = self.db.query(DictionaryModel)

    if language_id:
        query = query.filter(DictionaryModel.language_id == language_id)

    if concept_path_prefix:  # NEW
        query = query.join(ConceptModel).filter(
            ConceptModel.path.like(f"{concept_path_prefix}%")
        )

    return query.limit(limit).offset(offset).all()
```

**Обновить GraphQL schema:**
```python
@strawberry.field
def dictionaries(
    self,
    language_id: Optional[int] = None,
    concept_path_prefix: Optional[str] = None,  # NEW
    limit: int = 100,
    offset: int = 0
) -> List[DictionaryType]:
    # ...
```

**Effort:** 0.5 day (optional, можно обойтись без этого)

---

### Phase 2: Frontend Core (1 week)

#### #3 - Создать utility функции для переводов

**Файл:** `packages/frontend/src/lib/utils/i18n.ts`

```typescript
/**
 * Простая функция для получения перевода
 */
export function t(
  translations: Record<string, string>,
  key: string,
  fallback?: string
): string {
  return translations[key] || fallback || key;
}

/**
 * Преобразовать массив Dictionary в Map
 * Input: [{ concept: { name: "ui.nav.dashboard" }, name: "Dashboard" }, ...]
 * Output: { "ui.nav.dashboard": "Dashboard", ... }
 */
export function dictionariesToMap(dictionaries: Array<{
  concept: { name: string };
  name: string;
}>): Record<string, string> {
  return dictionaries.reduce((acc, dict) => {
    acc[dict.concept.name] = dict.name;
    return acc;
  }, {} as Record<string, string>);
}
```

**Effort:** 0.5 day

---

#### #4 - Создать Houdini GraphQL query

**Файл:** `packages/frontend/src/lib/graphql/GetUITranslations.gql`

```graphql
query GetUITranslations($languageId: Int!, $conceptPath: String) {
  dictionaries(
    languageId: $languageId
    conceptPathPrefix: $conceptPath
    limit: 500
  ) {
    concept {
      name
    }
    name
  }
}
```

Или inline в коде:
```typescript
import { graphql } from '$houdini';

export const GetUITranslations = graphql(`
  query GetUITranslations($languageId: Int!, $conceptPath: String) {
    dictionaries(languageId: $languageId, conceptPathPrefix: $conceptPath, limit: 500) {
      concept {
        name
      }
      name
    }
  }
`);
```

**Effort:** 0.5 day

---

#### #5 - Обновить +layout для загрузки глобальных переводов

**Файл:** `packages/frontend/src/routes/+layout.ts`

```typescript
import { GetUITranslations } from '$houdini';
import { languageStore } from '$lib/stores/languageStore.svelte';
import { dictionariesToMap } from '$lib/utils/i18n';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ fetch }) => {
  const languageId = languageStore.currentLanguageId || 1; // fallback to English

  // Загрузить переводы для navigation/header
  const navResult = await GetUITranslations.fetch({
    variables: {
      languageId,
      conceptPath: '/ui/nav'
    },
    fetch
  });

  // Загрузить общие переводы (buttons, common)
  const commonResult = await GetUITranslations.fetch({
    variables: {
      languageId,
      conceptPath: '/ui/common'
    },
    fetch
  });

  const buttonResult = await GetUITranslations.fetch({
    variables: {
      languageId,
      conceptPath: '/ui/button'
    },
    fetch
  });

  const navTranslations = dictionariesToMap(navResult.data?.dictionaries || []);
  const commonTranslations = dictionariesToMap(commonResult.data?.dictionaries || []);
  const buttonTranslations = dictionariesToMap(buttonResult.data?.dictionaries || []);

  // Объединить в один объект
  const globalTranslations = {
    ...navTranslations,
    ...commonTranslations,
    ...buttonTranslations
  };

  return {
    globalTranslations
  };
};
```

**Альтернатива (проще):** Загрузить все `/ui` переводы одним запросом:
```typescript
const result = await GetUITranslations.fetch({
  variables: {
    languageId,
    conceptPath: '/ui'  // все UI переводы
  },
  fetch
});
```

**Effort:** 1 day

---

#### #6 - Обновить AppHeader.svelte

**Файл:** `packages/frontend/src/lib/components/AppHeader.svelte`

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { useAuth } from '$lib/auth';
  import { goto } from '$app/navigation';
  import { t } from '$lib/utils/i18n';
  import LanguageSwitcher from './LanguageSwitcher.svelte';

  const auth = useAuth();
  let currentPath = $derived($page.url.pathname);

  // Получить переводы из layout
  const trans = $derived($page.data.globalTranslations || {});

  async function handleLogout() {
    await auth.logout();
    goto('/login');
  }

  function isActive(path: string): boolean {
    return currentPath === path;
  }
</script>

<nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex items-center space-x-8">
        <a href={auth.isAuthenticated ? '/dashboard' : '/'} class="text-2xl font-bold text-indigo-600">
          Multipult
        </a>

        {#if auth.isAuthenticated}
          <div class="hidden md:flex space-x-1">
            <a href="/dashboard" class="{isActive('/dashboard') ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300'} px-3 py-2 text-sm font-medium border-b-2 transition-colors">
              {t(trans, 'ui.nav.dashboard', 'Dashboard')}
            </a>
            <a href="/concepts" class="{isActive('/concepts') ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300'} px-3 py-2 text-sm font-medium border-b-2 transition-colors">
              {t(trans, 'ui.nav.concepts', 'Concepts')}
            </a>
            <a href="/languages" class="{isActive('/languages') ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300'} px-3 py-2 text-sm font-medium border-b-2 transition-colors">
              {t(trans, 'ui.nav.languages', 'Languages')}
            </a>
            <a href="/dictionaries" class="{isActive('/dictionaries') ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300'} px-3 py-2 text-sm font-medium border-b-2 transition-colors">
              {t(trans, 'ui.nav.dictionaries', 'Dictionaries')}
            </a>
          </div>
        {/if}
      </div>

      <div class="flex items-center space-x-4">
        <LanguageSwitcher />

        {#if auth.isAuthenticated}
          <div class="flex items-center space-x-3">
            <div class="text-right hidden sm:block">
              <p class="text-sm font-medium text-gray-900">{auth.user?.username}</p>
              <p class="text-xs text-gray-500">{auth.user?.email}</p>
            </div>

            <div class="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium">
              {auth.user?.username?.charAt(0).toUpperCase()}
            </div>
          </div>

          <button onclick={handleLogout} class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors">
            {t(trans, 'ui.button.logout', 'Logout')}
          </button>
        {:else}
          <a href="/login" class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">
            {t(trans, 'ui.button.signIn', 'Sign in')}
          </a>
          <a href="/register" class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-sm hover:shadow-md transition-all">
            {t(trans, 'ui.button.getStarted', 'Get Started')}
          </a>
        {/if}
      </div>
    </div>
  </div>
</nav>
```

**Effort:** 0.5 day

---

### Phase 3: Update Pages (1 week)

#### #7 - Home Page

**Файл:** `packages/frontend/src/routes/+page.ts`

```typescript
import { GetUITranslations } from '$houdini';
import { languageStore } from '$lib/stores/languageStore.svelte';
import { dictionariesToMap } from '$lib/utils/i18n';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, parent }) => {
  const { globalTranslations } = await parent();
  const languageId = languageStore.currentLanguageId || 1;

  const result = await GetUITranslations.fetch({
    variables: {
      languageId,
      conceptPath: '/ui/home'
    },
    fetch
  });

  const homeTranslations = dictionariesToMap(result.data?.dictionaries || []);

  return {
    homeTranslations,
    globalTranslations
  };
};
```

**Файл:** `packages/frontend/src/routes/+page.svelte`

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { useAuth } from '$lib/auth';
  import { goto } from '$app/navigation';
  import { t } from '$lib/utils/i18n';
  import { onMount } from 'svelte';

  const auth = useAuth();
  const trans = $derived($page.data.homeTranslations || {});

  onMount(() => {
    if (auth.isAuthenticated) {
      goto('/dashboard');
    }
  });
</script>

<svelte:head>
  <title>{t(trans, 'ui.home.title', 'Multipult - Multilingual Content Management')}</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
    <div class="text-center">
      <h1 class="text-5xl md:text-6xl font-extrabold text-gray-900 mb-6">
        {t(trans, 'ui.home.title', 'Multilingual Content')}
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
          {t(trans, 'ui.home.subtitle', 'Management')}
        </span>
      </h1>

      <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
        {t(trans, 'ui.home.description', 'Organize concepts, manage dictionaries, and handle multilingual content with ease.')}
      </p>

      <!-- Остальное аналогично, заменить все тексты на t() -->
    </div>
  </div>
</div>
```

**Effort:** 1 day

---

#### #8 - Остальные страницы

Повторить паттерн из #7 для:
- [ ] Dashboard (`/ui/dashboard`)
- [ ] Concepts (`/ui/concepts`)
- [ ] Languages (`/ui/languages`)
- [ ] Dictionaries (`/ui/dictionaries`)
- [ ] Login (`/ui/auth/login`)
- [ ] Register (`/ui/auth/register`)
- [ ] Forgot Password (`/ui/auth/forgotPassword`)

Для каждой страницы:
1. Создать `+page.ts` с load function
2. Загрузить переводы через `GetUITranslations` с нужным `conceptPath`
3. Обновить `+page.svelte` заменив hardcoded тексты на `t(trans, key, fallback)`

**Effort:** 2-3 days

---

### Phase 4: Реактивное переключение (1 day)

#### #9 - Auto-reload при смене языка

**Проблема:** При смене языка через `LanguageSwitcher` страница не обновляется автоматически.

**Решение:** Использовать `invalidateAll()` из SvelteKit.

**Обновить:** `packages/frontend/src/lib/stores/languageStore.svelte.ts`

```typescript
import { invalidateAll } from '$app/navigation';

class LanguageStore {
  private _currentLanguageId = $state<number | null>(null);

  get currentLanguageId(): number | null {
    return this._currentLanguageId;
  }

  setLanguage(languageId: number | null): void {
    this._currentLanguageId = languageId;

    if (typeof window !== 'undefined') {
      if (languageId !== null) {
        localStorage.setItem(STORAGE_KEY, languageId.toString());
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }

      // NEW: Invalidate all load functions to reload translations
      invalidateAll();
    }
  }

  // ... rest
}
```

**Альтернатива:** Использовать `$effect` в layout:

```typescript
// В +layout.svelte
$effect(() => {
  const langId = languageStore.currentLanguageId;
  if (langId && typeof window !== 'undefined') {
    invalidateAll();
  }
});
```

**Effort:** 0.5 day

---

## 📊 Summary

### Total Effort:
- **Phase 1 (Backend):** 1-1.5 days
- **Phase 2 (Frontend Core):** 2.5 days
- **Phase 3 (Update Pages):** 3-4 days
- **Phase 4 (Reactivity):** 0.5 day

**Total: 7-9 days (1.5-2 weeks) для одного разработчика**

---

## Checklist для тестирования

### Backend:
- [ ] Seed data создает UI-концепты с путями `/ui/...`
- [ ] Dictionary записи созданы для EN, RU, ES
- [ ] GraphQL query `dictionaries` с фильтром `conceptPathPrefix` работает

### Frontend:
- [ ] Переводы загружаются при старте приложения
- [ ] Header показывает переводы корректно
- [ ] Все страницы используют переводы
- [ ] Fallback работает (показывает ключ если перевод не найден)
- [ ] При смене языка интерфейс обновляется

### E2E:
- [ ] Пользователь открывает сайт → видит EN по умолчанию
- [ ] Меняет язык на RU → все тексты меняются на русский
- [ ] Переходит между страницами → переводы корректны
- [ ] Перезагружает страницу → выбранный язык сохранен
- [ ] Нет hardcoded текстов в UI

---

## Преимущества этого подхода

✅ **Минимум кода** - используем существующую инфраструктуру
✅ **Нет новых таблиц** - Dictionary уже есть
✅ **SvelteKit-native** - load functions, естественный data flow
✅ **Type-safe** - Houdini генерирует TypeScript типы
✅ **Простая поддержка** - один источник правды (БД)
✅ **Легко масштабируется** - добавить новый перевод = добавить Dictionary запись

---

## Следующие шаги (optional enhancements)

- [ ] **Кэширование:** Redis на backend, localStorage на frontend
- [ ] **Admin UI:** Страница для редактирования переводов
- [ ] **CLI:** Экспорт/импорт переводов в JSON/CSV
- [ ] **Интерполяция:** `t(trans, 'ui.greeting', { name: 'John' })` → "Hello, John!"
- [ ] **Плюрализация:** `tn(trans, 'ui.items', count)` → "1 item" / "2 items"

---

**Вывод:** Это действительно просто! Вы были правы. 🎉
