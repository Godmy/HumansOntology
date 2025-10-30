# ADR 0003: Frontend Icon Hygiene for Dashboard/Admin

- Status: Accepted
- Date: 2025-10-30
- Authors: Frontend Team

## Context

After the dashboard/admin refactor to Houdini stores, cards still rendered the correct numbers but the UI was littered with mojibake strings (`ЁЯФС`, `ЁЯСЛ`, etc.) inside Docker Desktop logs and in browsers without full emoji fonts. The root cause was a mix of legacy emoji literals (`🔑`, `📊`, `🌳`, etc.) and bespoke inline SVG arrows that bypassed our Tailwind design tokens. The situation also made it harder for AI maintainers to spot regressions because the same characters appeared in error logs when vite recompiled Svelte files.

## Decision

1. **Standard icon library**  
   Use `lucide-svelte` components for every icon on dashboard/admin pages (stats cards, quick actions, CTA banners). Icons are imported at the top-level script block and passed around as Svelte components (`<svelte:component this={stat.icon} />`), paired with `iconBg`/`iconColor` Tailwind classes.

2. **CTA consistency**  
   The admin CTA block now renders `<Key />` inside the gradient header and `<ArrowRight />` in the button. Plain emoji and hand-written SVGs are deprecated; all CTA visuals come from Lucide so that tree-shaking and theming stay predictable.

3. **Runes-safe data usage**  
   Keep `$props()`/`$derived` for Houdini stores (`GetDashboardStats`, `GetAdminStats`) and feed icon metadata via the same reactive arrays. This prevents accidental reintroduction of `export let` in runes mode and avoids empty stats when the store hasn’t resolved yet.

4. **Operational guidance**  
   Document the conventions in `docs/AI_COOKBOOK.md` so that future AI agents follow the same pattern when touching dashboard/admin views or related components.

## Consequences

- Eliminates mojibake in Docker Desktop and browser toolbars by sticking to a single icon source.
- Simplifies future icon swaps (just update the Lucide import) and keeps bundle size under control thanks to tree-shaking.
- Encourages consistent card structure between dashboard and admin routes, reducing the chance of mismatched layouts when Houdini data changes.
- Adds a small dependency on Lucide styling classes; teams must keep `lucide-svelte` up to date during dependency refreshes.

## References

- `packages/frontend/src/routes/dashboard/+page.svelte`
- `packages/frontend/src/routes/admin/+page.svelte`
- `docs/AI_COOKBOOK.md`
