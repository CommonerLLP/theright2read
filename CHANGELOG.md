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
- **`/spend/` rebuilt** as a lean, chart-led money page on the v2 system: per-capita
  by state, the libraries-vs-vanity comparison, and India-vs-world — as token-themed
  CSS bar charts (no chart library; light/dark for free) rendered from the verified
  data layer via the hexagonal ports (`assets/spend.js` → `RTR.ports`/`RTR.domain`).
  The full Quarto deep-dive is preserved at **`/spend/full/`**.
- `/inequality/` and the grammar-of-refusal essay themed via the bridge (dark mode).
- Masthead across all pages uses the campaign logo (mode-safe: white plate on dark).
- `/inequality/` timeline gains two verified beats: 2016 Chouhan-Cabinet
  recategorisation and 2019–20 NML declared "complete".

### Fixed
- `assets/core/ports.js` read globals off `window`, but `data.js` declares them as
  top-level `const` (lexical, not on `window`) — Dataset/Content ports returned empty.
  Now read via typeof-guarded bare identifiers; `/spend/` charts bind correctly.
- Deploy rule corrected (`CONTEXT.md`, local): production repo is
  `CommonerLLP/theright2read`, not the non-resolving `…/theright2read.github.io`.

### Removed / retired
- `/design/` (old "India Library Spend Tracker" prototype) → redirects to `/spend/`.
- `/writing/` → redirects to `/library/`.
- Dead `/data/` links (the `data/` dir is a gitignored symlink, never deployed).
- Unused `assets/rtr-mark.svg`.

### Deferred to v2.1
- `main.js` → ports migration for the legacy pages (timeline, calculator, dashboards
  still read globals + compute inline; `/spend/` is the first page on the ports).
- The Quarto `/spend/full/` deep-dive itself re-themed for dark mode (still light-only).
- DatasetPort → live multi-state fiscal JSON from `public-finance`.

## v1.0.0 — 2026-06 · Pre-revamp pamphlet

The original dark-pamphlet site: `/` (pamphlet), `/data/` (the present),
`/inequality/` (the history), `/design/` (spend prototype), `/writing/` (essays).
Bundled at the v1.0.0 tag before the v2 revamp.
