# Design — Django Kickstart (`django-kickstartx`)

A locked design system for the generated MVP starter templates (`base.html`, `home.html`, `about.html`). Every template and stylesheet reads this file before emitting code.

## Genre
modern-minimal

## Macrostructure family
- Marketing / Landing (`home.html`): **15 · Split Studio** (H2 Split Diptych hero + F3 Tabular spec/item registry + dark graphite quickstart band)
- Content / Architecture (`about.html`): **15 · Split Studio** (asymmetric two-column architecture overview + F3 Tabular stack specification sheet)
- Navigation: **N13 · Inline ⌘K search pill** (bordered top bar + working keyboard command palette for instant route/admin jumping)
- Footer: **Ft2 · Inline rule single line** (hairline top border, single-row colophon)

## Theme (`Cobalt`)
- `--color-paper`: `oklch(98.5% 0.004 250)`
- `--color-paper-2`: `oklch(95.5% 0.006 250)`
- `--color-paper-3`: `oklch(92.0% 0.008 250)`
- `--color-graphite`: `oklch(20.0% 0.016 260)`
- `--color-graphite-2`: `oklch(25.0% 0.018 260)`
- `--color-graphite-rule`: `oklch(32.0% 0.016 260)`
- `--color-graphite-ink`: `oklch(94.5% 0.006 250)`
- `--color-graphite-muted`: `oklch(72.0% 0.010 250)`
- `--color-ink`: `oklch(20.0% 0.020 258)`
- `--color-ink-2`: `oklch(34.0% 0.018 257)`
- `--color-muted`: `oklch(46.0% 0.014 255)`
- `--color-rule`: `oklch(88.5% 0.008 252)`
- `--color-rule-2`: `oklch(80.0% 0.012 252)`
- `--color-accent`: `oklch(55.0% 0.200 256)`
- `--color-accent-hover`: `oklch(49.0% 0.200 256)`
- `--color-accent-ink`: `oklch(98.5% 0.004 250)`
- `--color-focus`: `oklch(55.0% 0.200 256)`
- `--color-success`: `oklch(52.0% 0.150 155)`
- `--color-error`: `oklch(54.0% 0.190 28)`

## Typography
- Display: `"Space Grotesk"`, weight `600`, style `normal`, tracking `-0.03em`
- Body: `"IBM Plex Sans"`, weight `400` / `500`
- Outlier / Mono: `"JetBrains Mono"`, weight `400` / `500` (restricted to ≤ 2 roles: code/spec readout & kbd/status tags)
- Type scale anchor: `--text-display: clamp(2.25rem, 3.8vw + 1rem, 3.75rem)`

## Spacing
4-point named scale (`--space-3xs` through `--space-4xl`). Pages use named tokens (`var(--space-md)`), never raw pixel values.

## Motion
- Easings: `--ease-out: cubic-bezier(0.16, 1, 0.3, 1)`, `--ease-in: cubic-bezier(0.7, 0, 0.84, 0)`, `--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1)`
- Durations: `--dur-micro: 120ms`, `--dur-short: 220ms`, `--dur-long: 420ms`
- Reduced-motion fallback: opacity-only crossfade `≤ 150ms`

## CTA voice
- Primary CTA: solid `--color-accent` fill with `--color-accent-ink` text, `6px` technical radius (`--radius-control`), specific action verb
- Secondary CTA: `1px solid var(--color-rule-2)` outlined button on `--color-paper`, `6px` radius
