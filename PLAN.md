# Plan — Bardolino family guide

Locked before any agent runs. Do not renegotiate with the user.

## Trip physics

| Rule | Value |
| --- | --- |
| Base | Bardolino, Lake Garda, Italy |
| Pattern | Bardolino → day trip → Bardolino |
| Nights elsewhere | 0 |
| Days of stay | 6 |
| Trip menu | **~18–22 same-day loops** (browseable; family picks **5–6** across the stay) |
| Car | Yes, every day |
| Baby | Under 6 months |
| Stroller | Yes |
| Walking budget | ≤ 60 minutes easy walking |
| Drive cap | ~2 hours one way |
| Return | Before 18:00 |

Six days on site: expect **5–6 outing days** from the menu plus **two recovery / beach-at-base / nap days** at the apartment. Base days are acknowledged in the HTML (not as extra menu entries). Trip data lives in `shared/itinerary.json` (source of truth for the shipped guide).

## Priorities (user)

1. Beaches
2. Good food
3. Easy walks
4. Beautiful scenery
5. Stress-free travel

## Scoring weights (locked)

| Criterion | Weight |
| --- | --- |
| Parking | 20% |
| Baby friendliness | 20% |
| Beauty / scenery | 15% |
| Food | 15% |
| Walking comfort | 10% |
| Safety | 10% |
| Travel effort | 10% |

Each destination: integer **score / 100**, plus explanation, pros, cons, why suitable, why not suitable.

Formula:

```
score = round(
  parking * 0.20 +
  baby * 0.20 +
  beauty * 0.15 +
  food * 0.15 +
  walking * 0.10 +
  safety * 0.10 +
  effort * 0.10
)
```

Each criterion is 0–100. Higher **travel effort** score means *less* effort (easier).

## Mandatory trips

### 1. Venice

Must appear in the menu (mandatory flag).

The system **must decide the best way**. Compare at least:

- driving into the lagoon edge (Piazzale Roma / Tronchetto)
- parking outside Venice (Mestre / other mainland)
- train (especially via Peschiera del Garda or Desenzano)
- organized bus/boat tour from Lake Garda

Optimize for: infant, stroller/carrier, comfort, minimum stress, return before 18:00.

Do not automatically choose the obvious option.

### 2. Lake Garda boat / ferry day

Must appear in the menu (mandatory flag).

- Include a real Navigazione Laghi (or equivalent) boat/ferry experience
- May start from Bardolino or a nearby imbarcadero
- Need **not** be a full day
- Must return home before 18:00
- Car may remain in Bardolino — that is a feature

### Other menu entries

The remaining ~16–20 loops are scored selections from the research pool, surfaced as a browseable menu (not a locked four-day itinerary).

**Illegal justifications:** “It’s the most famous.” “Everyone does Sirmione.” “Gardaland is for families” (irrelevant for a 6-month-old).

**Legal justifications:** parking math, baby changing, shade, stroller surfaces, food quality, crowd timing, drive minutes.

## Research pool (minimum)

Agents must evaluate, not necessarily visit:

- Sirmione
- Lazise
- Garda / Punta San Vigilio / Baia delle Sirene
- Torri del Benaco
- Malcesine
- Riva del Garda
- Peschiera del Garda
- Desenzano
- Salò / Maderno / Gardone
- Valeggio sul Mincio / Borghetto / Sigurtà
- Verona
- Venice (mandatory)
- Bardolino-local beaches (Cisano, etc.) as *base-day* options — ideal for nap/recovery days, distinct from the mandatory ferry outing

Gardaland, Caneva, and theme parks are out of scope for a 6-month-old.

## Per-trip required fields

See `schemas/itinerary.schema.json`. Summary:

- name, score, why selected, difficulty, best departure, expected return
- driving distance & duration, route, parking location/cost/difficulty, Google Maps link
- walking route & duration, stroller friendliness, viewpoints, beaches, restaurants, coffee, hidden gems
- baby changing, rest places, stroller notes, crowds to avoid
- parking / food / tickets / ferry cost estimates
- rainy-day alternative

## HTML product

Single file: `output/bardolino-trip-guide.html`

Design target: Apple + Airbnb + Google Travel + Lonely Planet. Premium travel product.

Must include homepage hero, trip-menu overview, ranking, filters, expandable sections, timeline, comparison table, maps buttons, favorites, checklist, dark mode, print mode, mobile nav, packing, baby checklist, weather, etiquette, emergency, tourist traps, rainy-day plan. Venice and the Garda ferry day must be visible as mandatory picks in the menu.

## Suggested day-of-week logic (itinerary may apply)

- Venice: earliest weekday available (fewer crowds than weekend)
- Ferry: pick a calm weather window; have a land backup
- Gardens / Borghetto: any day; Monday check restaurant closures
- Beach / fortress town: morning parking advantage

## Done when

A family can execute the holiday from the HTML file alone, including where to park, when to leave, what to carry for the baby, and what to do if it rains.
