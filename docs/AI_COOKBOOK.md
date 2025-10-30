# AI Cookbook: Diagnosing Dashboard/Admin Zero Data

Цель: дать быстрый чек-лист для ИИ-агентов и разработчиков, чтобы они не бегали по коду наугад, когда дашборд и админка показывают `0` или грузятся по несколько секунд.

---

## 1. Бэкенд: проверяем логирование

1. **Папка логов** – `packages/backend/logs/` монтируется в контейнеры (см. ADR-0001). Нас интересуют `app.log` и `access.log`.
2. **Health** – убедитесь, что `/health` отвечает без ошибок. В логах должны мелькать строки вида:  
   `"[request_id] GET /graphql/ 200 (XXXms) user_id=..."`.
3. **Payload** – если видите `body={"query": "...dashboardStats..."}` и рядом `200`, значит GraphQL принял запрос. Если статус `4xx`, проверьте заголовки авторизации.
4. **Медленные запросы** – `WARNING Slow query (...)` сигнализирует о тяжёлых select’ах. Сейчас это нормально (агрегаты на больших таблицах), но держите в голове: троттлинг можно решать индексами или бэкграунд-кэшированием.

## 2. Бэкенд: проверяем данные напрямую

1. **GraphQL вручную**  
   ```powershell
   Invoke-RestMethod `
     -Uri http://127.0.0.1:8000/graphql/ `
     -Method Post `
     -Body '{"query":"query { dashboardStats { concepts languages dictionaries } }"}' `
     -ContentType 'application/json'
   ```
   В ответе должны быть числа (например `3084`). Если `null/{}`
   - Проверьте, что сиды зашли (`docker exec humansontology_db_dev psql ... "SELECT COUNT(*) FROM concepts;"`).
   - Посмотрите в логах `scripts.seed_data` — может, сиды завершились с кодом `1`.
2. **Seed retry** – если надо прогнать сиды ещё раз, используйте `docker compose exec backend python scripts/seed_data.py --force`. Обновлённый скрипт (ADR-0001) теперь возвращает код выхода и не валит контейнер.

## 3. Фронтенд: Svelte + Houdini

1. **Генерация артефактов** – после любой правки `.gql`: `yarn generate`. Если схема поменялась – `npx houdini pull-schema` (или `yarn generate --pull-schema`).  
   Артефакты лежат в `.houdini/artifacts`, а в `.houdini/graphql/schema.graphql` хранится SDL.
2. **Svelte runes (`$props`, `$derived`)** – в режиме runes нельзя использовать `export let`. Для маршрута:
   ```svelte
   const statsStore = data.GetDashboardStats;
   const stats = $derived($statsStore?.data ?? {});
   ```
   и уже в шаблоне – `stats.counts?.concepts`.  
   Ошибка “`export let` in runes mode” → перепишите на `$props`.
3. **Полезный лог в консоль** – временно вставьте:
   ```svelte
   console.log('[Dashboard] Houdini store snapshot', $statsStore);
   ```
   Если приходит `{data:{counts:{...}}}`, проблема в отрисовке. Если `{}`, значит запрос не вернул данные.
4. **Урезаем запросы ради перфоманса** – тяжелые страницы (dashboard) должны тянуть только агрегаты. Пример в `src/routes/dashboard/+page.gql`:  
   ```graphql
   query GetDashboardStats {
     counts: dashboardStats { concepts languages dictionaries }
   }
   ```
   Если видите, что тянутся тысячи записей – обрежьте запрос и перегоните Houdini (`yarn generate`). Это делали в патчах 2025-10-30.

## 4. Общие приёмы

- **После смены схемы** – перезапустите фронтовый контейнер (`docker compose restart frontend`), иначе Vite может долго держать старые артефакты.
- **Если дашборд/админка всё ещё показывают `0`** – проверьте, что в браузере запросы уходят на `/graphql/` с авторизацией. Иногда редирект с `/graphql` на `/graphql/` срезает заголовок `Authorization`.
- **Документируйте изменения** – добавляйте заметки в ADR-0002 и сюда, чтобы следующая модель знала, где “подтянуть язык”.

## 5. UI: Lucide вместо эмодзи

- **Статистика и быстрые действия** — на packages/frontend/src/routes/dashboard/+page.svelte для карточек статистики и быстрого доступа используем иконки lucide-svelte (BookOpen, Languages, Library, Shield, Plus, Globe2, NotebookPen) с цветами iconBg/iconColor. Эмодзи порождают артефакты вроде ЁЯФС в Docker Desktop и ломают рендер.
- **CTA «Admin Panel»** — в том же файле блок администратора собираем через <Key /> в градиентной карточке и <ArrowRight /> в кнопке. Инлайн svg и 🔑 больше не используем, чтобы избегать ite-plugin-svelte предупреждений.
- **Админка** — файл packages/frontend/src/routes/admin/+page.svelte держим на тех же соглашениях (icon, iconBg, iconColor, $props(), $derived). Это гарантирует, что Houdini store с GetAdminStats не обнуляется.
- **Регрессии** — после правок прогоняем yarn dev и проверяем, что карточки Dashboard/Admin появляются вместе с данными и в консоли нет [plugin:vite-plugin-svelte:compile].


---

### История обновлений
- 2025-10-30: зафиксировано ускорение дашборда (запрос тянет только агрегаты) и переход на чтение данных через Houdini store; наблюдаются кейсы, когда UI всё ещё отображает нули – см. шаги выше для диагностики.
- 2025-10-30 (вечер): фронтенд переведён на использование `$dashboardStatsStore?.data?.counts`, старые обращения к `data.GetDashboardStats?.concepts` удалены. Если снова увидите нули — проверьте, что шаблон опирается именно на Houdini store, а не на закешированное поле исходного `data`.
- 2025-10-30 (позже): аналогичный паттерн применён к страницам `languages`, `concepts`, `dictionaries` — всё, что приходит из `load_Get*`, читаем через `$store?.data`. Если видите пустые списки, проверьте, не осталось ли прямых обращений `data.GetXxx`.
