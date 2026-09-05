# UI specification — Bardolino family guide

Single file, offline, mobile-first. Feel: a small travel studio, not a blog and not an admin dashboard.

## Brand

**Wordmark:** `Bardolino` in display serif, subtitle `Six days · four loops · home before dinner`.

**Palette**

| Token | Light | Dark |
| --- | --- | --- |
| `--ink` | `#0B3A4A` | `#E7F0F2` |
| `--water` | `#1C6B7A` | `#7EC8D4` |
| `--foam` | `#F6F1E8` | `#0A161C` |
| `--sand` | `#E4D3B4` | `#1B2C34` |
| `--terra` | `#C45C26` | `#E08A55` |
| `--gold` | `#C4A574` | `#C4A574` |
| `--card` | `#FFFbf5` | `#13242C` |

**Type:** `ui-sans-serif, system-ui, sans-serif` for UI; `"Palatino Linotype", Palatino, Georgia, serif` for the wordmark and trip titles.

**Illustration:** CSS/SVG lake horizon with a small ferry silhouette. No remote images.

## Landmarks

1. Skip link
2. `header` sticky: wordmark, anchor nav (Trips, Compare, Pack, Practical), favorite count, theme toggle, print
3. Mobile: hamburger that opens a full-screen sheet
4. `main`
5. `footer` disclaimer

## Homepage stack

### Hero

Eyebrow: `Lake Garda · family edition`
H1: `Four day trips. Apartment every night.`
Lead: one sentence on Bardolino base, baby, 18:00 rule.
Fact chips: `6 days` `Car` `Stroller` `Baby < 6 months` `Back by 18:00`

### Ranking

Horizontal list of four score marks (number in a ring). Sorted by score. Caption: `Ranked for parking, baby, beauty, food, walking, safety, effort — not for fame.`

### Filters

Chips: All · Beach · Food · Easiest · Boat · City  
Empty state: `Nothing in this filter. The four trips are still below if you reset.`

### Trip cards (4)

Always visible: name, score, leave–return, drive km, difficulty, parking difficulty, 4 highlights, favorite heart, `Open trip` button.

### Operating rules (expanded by default)

Nap at home, carrier vs stroller, verify trains/ferries tonight.

## Trip chapters

One `section` per trip, `id="trip-{id}"`.

Order on page: ranking order (Sigurtà, ferry, Peschiera, Venice) so the easiest wins sit first; Venice is last because it is the hard day, not because it is unimportant. Note that Venice is mandatory in a small pill.

Sub-nav inside chapter: Timeline · Transport · Experience · Family · Costs · Backup

Venice chapter includes a **mode comparison** table (A–D) with the winner highlighted.

Parking block is a card, not a footnote: lot name, cost, difficulty, backup, maps button + address text.

## Comparison table

Rows: Score, Leave, Return, Drive, Parking, Stroller, Beach, Food highlight, Difficulty.

Sticky first column on mobile (horizontal scroll).

## Checklists

Packing and baby lists. Checkbox + `localStorage` key `bardolino-checklist`. Progress `n/m packed`.

## Practical

Weather, etiquette, traps, rainy, emergency (112 / 118 / Via Croce seasonal studio / Pederzoli pointer).

## Interaction

| Feature | Spec |
| --- | --- |
| Theme | `bardolino-theme`: `light` \| `dark`. Toggle. Respect `prefers-color-scheme` on first visit. |
| Favorites | `bardolino-favorites` array of trip ids. Heart on cards. |
| Filters | Show/hide `[data-trip]` via `data-tags`. |
| Accordion | `<details>` for sub-blocks; print forces `open`. |
| Print | Hide nav/toggles, expand details, light colors, show maps URLs as text. |
| Reduced motion | Disable hero drift and smooth-scroll. |

## Empty / error

- Filter empty: reset button
- localStorage missing (private mode): features still work in-memory

## Accessibility

Contrast on foam/ink. `:focus-visible` rings. Buttons have text. Score rings have numeric text, not color-only.

## Frontend must not

Use React, Tailwind CDN, Google Fonts, Unsplash, or a service worker.
