# Отображение онтологии человека на Frontend

## 📋 Обзор

После инициализации БД у вас есть полная онтология аттракторов человека (~11000-15000 концептов).
Этот документ описывает, как отобразить эту иерархию на главной странице frontend.

---

## 🗂️ Структура данных

### Модели

#### ConceptModel (таблица `concepts`)
```typescript
interface Concept {
  id: number;
  path: string;          // "1.1.1.1.1." - уникальный путь
  depth: number;         // Глубина в дереве (0-10)
  parent_id: number | null;  // Ссылка на родителя
  children?: Concept[];  // Дочерние концепты (для дерева)
}
```

#### DictionaryModel (таблица `dictionaries`)
```typescript
interface Dictionary {
  id: number;
  concept_id: number;    // Ссылка на концепт
  language_id: number;   // Ссылка на язык
  name: string;          // Название (русский текст)
  description: string | null;  // JSON с характеристиками
}
```

---

## 🎯 Примеры путей в онтологии

```
1.                                          # Точечные аттракторы
├─ 1.1.                                     # Молекулярный уровень
│  ├─ 1.1.1.                               # Концентрационные аттракторы
│  │  ├─ 1.1.1.1.                          # Энергетические концентрационные аттракторы
│  │  │  ├─ 1.1.1.1.1.                     # Аттракторы концентрации АТФ/АДФ
│  │  │  │  ├─ 1.1.1.1.1.1.                # Митохондриальные АТФ/АДФ аттракторы
│  │  │  │  │  ├─ 1.1.1.1.1.1.1.           # Матриксные аттракторы
│  │  │  │  │  │  ├─ 1.1.1.1.1.1.1.1.      # Субстратные комплексы
│  │  │  │  │  │  ├─ 1.1.1.1.1.1.1.2.      # Ферментные комплексы
│  │  │  │  │  │  └─ 1.1.1.1.1.1.1.3.      # Регуляторные комплексы
```

---

## 🚀 GraphQL запросы

### 1. Корневые концепты (depth = 0)

```graphql
query GetRootConcepts {
  concepts(filters: { depth: 0 }) {
    id
    path
    depth
    dictionaries {
      name
      language {
        code
      }
    }
  }
}
```

### 2. Дочерние концепты

```graphql
query GetChildConcepts($parentId: Int!) {
  concepts(filters: { parentId: $parentId }) {
    id
    path
    depth
    parent_id
    dictionaries(languageCode: "ru") {
      name
      description
    }
  }
}
```

### 3. Полное дерево (осторожно, может быть большим!)

```graphql
query GetFullTree($depth: Int!) {
  concepts(filters: { depth: { lte: $depth } }) {
    id
    path
    depth
    parent_id
    dictionaries(languageCode: "ru") {
      name
      description
    }
  }
}
```

### 4. Поиск концептов

```graphql
query SearchConcepts($search: String!) {
  searchConcepts(query: $search, languageCode: "ru") {
    id
    path
    depth
    score
    dictionaries {
      name
      description
    }
  }
}
```

---

## 🎨 Компоненты React

### 1. Простой список (для начала)

```tsx
// components/ConceptList.tsx
import { useQuery } from '@apollo/client';
import { GET_ROOT_CONCEPTS } from './queries';

export function ConceptList() {
  const { data, loading } = useQuery(GET_ROOT_CONCEPTS);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="concept-list">
      <h2>Онтология аттракторов человека</h2>
      <ul>
        {data.concepts.map(concept => (
          <li key={concept.id}>
            <strong>{concept.path}</strong>
            {' - '}
            {concept.dictionaries.find(d => d.language.code === 'ru')?.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 2. Дерево с раскрытием (рекомендуется)

```tsx
// components/ConceptTree.tsx
import { useState } from 'react';
import { useQuery } from '@apollo/client';
import { ChevronRight, ChevronDown } from 'lucide-react';

interface ConceptNodeProps {
  concept: Concept;
  language: string;
}

function ConceptNode({ concept, language }: ConceptNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { data, loading } = useQuery(GET_CHILD_CONCEPTS, {
    variables: { parentId: concept.id },
    skip: !isExpanded,
  });

  const name = concept.dictionaries.find(d => d.language.code === language)?.name;

  return (
    <div className="concept-node">
      <div
        className="concept-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ paddingLeft: `${concept.depth * 20}px` }}
      >
        {isExpanded ? <ChevronDown /> : <ChevronRight />}
        <span className="concept-path">{concept.path}</span>
        <span className="concept-name">{name}</span>
      </div>

      {isExpanded && !loading && data?.concepts && (
        <div className="concept-children">
          {data.concepts.map(child => (
            <ConceptNode
              key={child.id}
              concept={child}
              language={language}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function ConceptTree() {
  const { data, loading } = useQuery(GET_ROOT_CONCEPTS);

  if (loading) return <div>Загрузка онтологии...</div>;

  return (
    <div className="concept-tree">
      <h1>Онтология аттракторов человеческого организма</h1>
      <div className="tree-content">
        {data?.concepts.map(concept => (
          <ConceptNode
            key={concept.id}
            concept={concept}
            language="ru"
          />
        ))}
      </div>
    </div>
  );
}
```

### 3. С использованием библиотеки react-d3-tree

```tsx
// components/ConceptVisualization.tsx
import Tree from 'react-d3-tree';
import { useMemo } from 'react';

export function ConceptVisualization() {
  const { data } = useQuery(GET_FULL_TREE, {
    variables: { depth: 3 }  // Ограничим глубину для производительности
  });

  // Преобразуем в формат react-d3-tree
  const treeData = useMemo(() => {
    if (!data) return null;

    const buildTree = (parentId: number | null) => {
      return data.concepts
        .filter(c => c.parent_id === parentId)
        .map(concept => ({
          name: concept.dictionaries[0]?.name || concept.path,
          attributes: {
            path: concept.path,
            depth: concept.depth,
          },
          children: buildTree(concept.id),
        }));
    };

    return {
      name: 'Онтология человека',
      children: buildTree(null),
    };
  }, [data]);

  if (!treeData) return <div>Загрузка...</div>;

  return (
    <div style={{ width: '100%', height: '800px' }}>
      <Tree
        data={treeData}
        orientation="horizontal"
        translate={{ x: 100, y: 400 }}
        nodeSize={{ x: 200, y: 50 }}
      />
    </div>
  );
}
```

---

## 📊 Рекомендации по производительности

### 1. Ленивая загрузка (Lazy Loading)

✅ **Рекомендуется**: Загружать дочерние узлы только при раскрытии

```tsx
// Загружаем только при клике
const { data } = useQuery(GET_CHILD_CONCEPTS, {
  variables: { parentId },
  skip: !isExpanded,  // Не загружать пока не раскрыт
});
```

❌ **Не рекомендуется**: Загружать все 11000+ узлов сразу

### 2. Виртуализация

Для больших списков используйте `react-window` или `react-virtualized`:

```tsx
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={concepts.length}
  itemSize={50}
>
  {({ index, style }) => (
    <div style={style}>
      {concepts[index].name}
    </div>
  )}
</FixedSizeList>
```

### 3. Кэширование

```tsx
import { useQuery } from '@apollo/client';

const { data } = useQuery(GET_CONCEPTS, {
  fetchPolicy: 'cache-first',  // Использовать кэш
});
```

### 4. Пагинация

```graphql
query GetConcepts($page: Int!, $limit: Int!) {
  concepts(
    pagination: { page: $page, limit: $limit }
    filters: { depth: 0 }
  ) {
    nodes {
      id
      path
      dictionaries { name }
    }
    totalCount
  }
}
```

---

## 🎨 Примеры UI

### Вариант 1: Аккордеон (простой)

```
▼ 1. Точечные аттракторы (4000-5000)
  ▼ 1.1. Молекулярный уровень
    ▶ 1.1.1. Концентрационные аттракторы
    ▶ 1.1.2. Конформационные аттракторы
  ▶ 1.2. Клеточный уровень
▶ 2. Периодические аттракторы (100-135)
▶ 3. Квазипериодические аттракторы (210-255)
```

### Вариант 2: Боковая панель + детали

```
┌──────────────┬────────────────────────────┐
│              │ Молекулярный уровень       │
│ 1. Точечные  │                           │
│  └ 1.1. Мол. │ Описание:                 │
│     ├ 1.1.1. │ Концентрационные и        │
│     └ 1.1.2. │ конформационные           │
│              │ аттракторы на             │
│ 2. Периодич. │ молекулярном уровне       │
│              │                           │
│ 3. Квазипер. │ Характеристики:          │
│              │ • Количество: 1600-2000   │
└──────────────┴────────────────────────────┘
```

### Вариант 3: Граф (визуализация)

Используйте библиотеки:
- `react-d3-tree` - дерево
- `react-flow` - граф
- `vis-network` - сетевая визуализация

---

## 🔍 Поиск и фильтрация

### Поиск по названию

```tsx
function ConceptSearch() {
  const [search, setSearch] = useState('');
  const { data } = useQuery(SEARCH_CONCEPTS, {
    variables: { search },
    skip: search.length < 3,
  });

  return (
    <div>
      <input
        type="text"
        placeholder="Поиск концептов..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      {data?.searchConcepts.map(concept => (
        <div key={concept.id}>
          <span>{concept.path}</span>
          {' - '}
          <span>{concept.dictionaries[0]?.name}</span>
        </div>
      ))}
    </div>
  );
}
```

### Фильтрация по глубине

```tsx
<select onChange={e => setDepth(e.target.value)}>
  <option value="">Все уровни</option>
  <option value="0">Уровень 1 (корень)</option>
  <option value="1">Уровень 2</option>
  <option value="2">Уровень 3</option>
</select>
```

---

## 📱 Адаптивность

### Desktop
- Полное дерево с раскрытием
- Боковая панель + детали

### Tablet
- Упрощенное дерево
- Модальное окно для деталей

### Mobile
- Список с аккордеоном
- Поиск в приоритете

---

## 🎯 Рекомендуемый подход для начала

### Этап 1: Простой список корневых концептов
```tsx
// Просто покажите 7 основных категорий
<ConceptList depth={0} />
```

### Этап 2: Добавьте раскрытие
```tsx
// Дерево с lazy loading
<ConceptTree />
```

### Этап 3: Добавьте поиск
```tsx
<ConceptSearch />
```

### Этап 4: Визуализация (опционально)
```tsx
<ConceptVisualization />
```

---

## 📚 Библиотеки

Рекомендуемые библиотеки для работы с деревьями:

1. **react-d3-tree** - Визуализация дерева (D3.js)
   ```bash
   npm install react-d3-tree
   ```

2. **react-arborist** - Мощное виртуализированное дерево
   ```bash
   npm install react-arborist
   ```

3. **antd Tree** - UI компонент дерева
   ```bash
   npm install antd
   ```

4. **react-window** - Виртуализация для производительности
   ```bash
   npm install react-window
   ```

---

## ✅ Чек-лист реализации

- [ ] Создать GraphQL запросы для концептов
- [ ] Компонент для отображения корневых концептов
- [ ] Компонент дерева с раскрытием
- [ ] Поиск по концептам
- [ ] Фильтрация по глубине/категории
- [ ] Отображение характеристик концепта
- [ ] Мультиязычность (ru/en/es)
- [ ] Адаптивный дизайн
- [ ] Оптимизация производительности

---

## 🎉 Итог

После реализации пользователи смогут:
- ✅ Просматривать полную онтологию человека на главной странице
- ✅ Раскрывать/сворачивать узлы дерева
- ✅ Искать по концептам
- ✅ Видеть характеристики каждого аттрактора
- ✅ Переключать языки интерфейса

**Вся онтология доступна и готова к отображению!** 🚀
