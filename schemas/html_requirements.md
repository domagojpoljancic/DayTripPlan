# HTML requirements

The only user-facing artifact is:

```
output/bardolino-trip-guide.html
```

## File rules

| Rule | Requirement |
| --- | --- |
| Count | Exactly one HTML file |
| CSS | Embedded in `<style>` |
| JavaScript | Embedded in `<script>` |
| Frameworks | None |
| Build | None |
| Fonts | System stack only (no Google Fonts, no downloaded woff) |
| Images | Inline SVG or CSS only (no remote images) |
| Offline | Usable via `file://` with network disabled |
| Maps | Buttons may point at `https://maps.google.com/...` but the address/lot name must remain visible as text |
| Responsive | Mobile-first |
| Print | `@media print` stylesheet; expandable content visible |

## Document

- `lang="en"`
- Semantic landmarks: `header`, `nav`, `main`, `footer`
- Skip-to-content link
- Unique `h1`

## Homepage must include

- Hero (place, stay length, promise: home before 18:00)
- Family facts (baby, stroller, car, apartment)
- Overview of **four** trips
- Trip ranking by score
- Filter chips

## Each trip card must show without expanding

- Name
- Score /100
- Duration (leave–return)
- Distance
- Difficulty
- 3–5 highlights
- Parking difficulty
- Favorite toggle

## Each trip detail must include

- Why selected
- Best departure / expected return
- Timeline
- Transport: distance, duration, route, parking location, parking cost, parking difficulty, maps button
- Walking route + duration
- Stroller friendliness
- Viewpoints, beaches, restaurants, coffee, hidden gems
- Baby changing, rest spots, stroller notes, crowds to avoid
- Costs: parking, food, tickets, ferry
- Rainy-day alternative
- Venice only: comparison of driving / park-outside / train / organized transport and the **decision**

## Interactive

- Filters
- Expandable sections
- Timeline view
- Comparison table of the four trips
- Maps buttons
- Favorites (`localStorage`)
- Checklist (`localStorage`)
- Dark mode
- Print
- Mobile navigation

## Utility content

- Packing checklist
- Baby checklist
- Weather considerations
- Local etiquette
- Emergency information (112 / 118, Bardolino medical notes, nearest ER pointer)
- Tourist traps / things to avoid
- Rainy-day plan

## Design quality

Must not look like a default markdown convert. Large display type, calm lake palette, generous spacing, score as a product metric, cards with clear hierarchy.

Forbidden phrases: “Welcome to your app”, “As an AI”, lorem ipsum.

## QA grep (orchestrator / QA should run)

Fail if the HTML contains:

- `cdn.`
- `unpkg`
- `fonts.googleapis`
- `tailwindcss`
- `react`
- more than four `data-trip-id` (or equivalent) trip records
