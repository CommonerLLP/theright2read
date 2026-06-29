# Changelog

All notable changes to the theright2read.org site. Newest first.

## v2.0.0 — 2026-06-29 · Campaign design system + hexagonal re-architecture

Breaking visual + architecture change. One identity across the site, the Working
Papers, and the Briefs; mobile-first; light + dark mode; FOSS assets.

### Added
- **Design system** (`assets/tokens.css`): single source of truth for palette,
  type, spacing — light + dark as first-class semantic roles. `assets/theme.js`
  (no-flash, persisted toggle, system-aware).
- **Shared components** (`assets/campaign.css`): masthead, nav, flag, buttons,
  cards, big-numbers — used by the site and the web Briefs.
- **Hexagonal core**: `assets/core/domain.js` (pure computations, node-tested) and
  `assets/core/ports.js` (Design / Content / Dataset / Chart / Publications ports).
- **`/play/`** — games hub (Higher-or-Lower + Statue Test, "What Did We Build?")
  with a challenge-a-friend share row. Games now live on a tracked, deployed page.
- **`/library/`** — reading room (publications index), replacing `/writing/`.
- **Home deferral section** — "Promised as a commons, delivered as a deferral":
  the systematic-deferral history, lead-linked to the full `/inequality/` timeline.
- **`legacy-bridge.css`** — themes the original `styles.css` pages with v2 tokens
  + dark mode, with no per-page rewrite.
- Campaign logo as favicon (svg + png set).

### Changed
- Home `/` rebuilt on the v2 system (calculator, letter, actions preserved).
- `/inequality/` and the grammar-of-refusal essay themed via the bridge (dark mode).
- Masthead across all pages uses the campaign logo (mode-safe: white plate on dark).
- `/inequality/` timeline gains two verified beats: 2016 Chouhan-Cabinet
  recategorisation and 2019–20 NML declared "complete".

### Removed / retired
- `/design/` (old "India Library Spend Tracker" prototype) → redirects to `/spend/`.
- `/writing/` → redirects to `/library/`.
- Dead `/data/` links (the `data/` dir is a gitignored symlink, never deployed).
- Unused `assets/rtr-mark.svg`.

### Deferred to v2.1
- Full v2 redesign of the Quarto `/spend/` deep-dive (lean, chart-led, dark mode).
- `main.js` → ports migration; DatasetPort/ChartPort-driven SVG charts.

## v1.0.0 — 2026-06 · Pre-revamp pamphlet

The original dark-pamphlet site: `/` (pamphlet), `/data/` (the present),
`/inequality/` (the history), `/design/` (spend prototype), `/writing/` (essays).
Bundled at the v1.0.0 tag before the v2 revamp.
