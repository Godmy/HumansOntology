# План интеграции Svelte Flow

Этот документ описывает шаги для интеграции библиотеки [Svelte Flow](https://svelteflow.dev/) в наш фронтенд-проект для создания интерактивных диаграмм и node-based интерфейсов.

## 1. Установка зависимостей

Первым шагом необходимо добавить библиотеку `@sveltejs/flow` в зависимости фронтенд-приложения.

**Действие:**
Выполнить команду в директории `packages/frontend`:
```bash
yarn add @sveltejs/flow
```

## 2. Создание компонента-обертки

Чтобы обеспечить переиспользуемость и инкапсулировать логику работы с Svelte Flow, создадим компонент-обертку.

**Действие:**
Создать новый файл: `packages/frontend/src/lib/components/workflow/SvelteFlowCanvas.svelte`.

## 3. Базовая реализация в компоненте

В созданном компоненте `SvelteFlowCanvas.svelte` добавим базовую настройку для отображения поля с несколькими узлами.

**Действие:**
Добавить следующий код в `SvelteFlowCanvas.svelte`:

```svelte
<script lang="ts">
  import { SvelteFlow, Controls, Background } from '@sveltejs/flow';
  import { writable } from 'svelte/store';

  import '@sveltejs/flow/dist/style.css';

  // Начальные узлы
  const initialNodes = writable([
    {
      id: '1',
      type: 'input',
      data: { label: 'Начальный узел' },
      position: { x: 250, y: 5 }
    },
    {
      id: '2',
      data: { label: 'Промежуточный узел' },
      position: { x: 100, y: 100 }
    },
    {
      id: '3',
      type: 'output',
      data: { label: 'Конечный узел' },
      position: { x: 400, y: 100 }
    }
  ]);

  // Начальные связи
  const initialEdges = writable([
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3' }
  ]);
</script>

<div style="height: 80vh; width: 100%;">
  <SvelteFlow nodes={initialNodes} edges={initialEdges} fitView>
    <Controls />
    <Background />
  </SvelteFlow>
</div>

```

## 4. Интеграция на страницу

Для проверки создадим новую тестовую страницу и разместим на ней наш компонент.

**Действие:**
1.  Создать новый роут (страницу), например, `packages/frontend/src/routes/test/workflow/+page.svelte`.
2.  Импортировать и отобразить компонент `SvelteFlowCanvas`:

```svelte
<script lang="ts">
  import SvelteFlowCanvas from '$lib/components/workflow/SvelteFlowCanvas.svelte';
</script>

<h1>Тестирование Svelte Flow</h1>

<SvelteFlowCanvas />

```

## 5. Верификация

После выполнения всех шагов необходимо запустить dev-сервер и убедиться, что компонент корректно отображается.

**Действие:**
1.  Перейти в директорию `packages/frontend`.
2.  Запустить команду `yarn dev`.
3.  Открыть в браузере страницу `/test/workflow`.

**Ожидаемый результат:**
На странице отображается интерактивное поле с тремя узлами и связями между ними. Пользователь может перемещать узлы и масштабировать вид.
