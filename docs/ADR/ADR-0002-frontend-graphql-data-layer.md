# ADR 0002: Frontend GraphQL Data Layer with SvelteKit + Houdini

- Status: Accepted
- Date: 2025-10-30
- Authors: Frontend Team

## Context

The web client is built with SvelteKit, Vite, TypeScript, Tailwind, and GraphQL endpoints served by the backend. To keep data fetching declarative and type-safe we evaluated raw fetches, urql, Apollo, and Houdini. We also needed SSR-friendly behaviour and a predictable place to store generated artifacts.

## Decision

1. **GraphQL client**  
   Adopt Houdini + `houdini-svelte` for query/mutation codegen, cache management, and SvelteKit integration.

2. **Schema management**  
   Store introspection output in `.houdini/graphql/schema.json` and the printed SDL in `.houdini/graphql/schema.graphql`. Use `npx houdini pull-schema` (or `yarn generate --pull-schema`) against the backend (`http://127.0.0.1:8000/graphql/`) so contributors stay in sync.

3. **Artifacts and naming**  
   Keep GraphQL documents near their routes/components (`*.gql`). Each operation name must be unique project-wide. Houdini artifacts live under `.houdini/artifacts/` and are committed. When slicing an operation to improve performance (e.g. returning only aggregates for the dashboard to avoid loading thousands of records), regenerate artifacts so downstream stores are in sync.

4. **Runtime usage**  
   Routes use the generated `load_<Operation>` helpers, while components receive data via props instead of triggering duplicate fetches. Components that need client-side refresh can import `graphql` tagged queries and call `.fetch` manually, but they should not redefine operations already used by the route layer. В режиме runes Houdini передаёт сторы: сохраняйте ссылку (`const statsStore = data.GetDashboardStats`) и далее в вычислениях обращайтесь к `$statsStore?.data`. Прямое чтение `statsStore.data` возвращает пустой снимок и приводит к «нулевым» картинкам на дашбордах.

5. **Developer workflow**  
   - `yarn generate` after changing any `.gql` file or when backend schema shifts.  
   - `yarn prepare` (already run by Git hooks) to resync SvelteKit and Houdini.  
   - Avoid editing `.houdini` artifacts manually; update source `.gql` or backend schema instead.
   - When debugging “blank dashboards”, dump `$store` values in the browser console. If they are `{data:{counts:{...}}}`, the issue is rendering. If they are `{}`, check authentication headers or whether the backend query was trimmed too aggressively.

## Consequences

- Strict typing across queries, stores, and components via generated `.d.ts` files.
- Reduced runtime errors (e.g., missing exports) thanks to consistent generation.
- Requires contributors to keep schema/artifacts up to date; CI should include `yarn generate && git diff --exit-code`.
- Enforces single responsibility: routes fetch data, components focus on presentation.

## References

- `packages/frontend/houdini.config.js`
- `.houdini/artifacts/` and `.houdini/graphql/`
- `src/routes/**/+page.gql`, `src/routes/**/+page.ts`
- `docs/AI_COOKBOOK.md`
