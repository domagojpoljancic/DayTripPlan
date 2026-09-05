# QA report

## Verdict

PASS_WITH_NOTES

The HTML is a single offline file with exactly four Bardolino loops, a compared Venice access mode, a short ferry day, honest scores, named parking, and the required utility sections. Blocking travel errors were not found after polish (print expands details; maps URLs remain visible as text).

## Blocking

- [x] ~~None remaining.~~ Four trips, all return before 18:00 (latest 17:25 Venice).
- [x] Venice compares driving / Mestre / Peschiera train / coach; train wins.
- [x] Ferry is Navigazione Laghi from Bardolino, not a Riva endurance cruise.
- [x] No CDN / Google Fonts / frameworks.
- [x] Parking lots named on every trip, with cost and backup.
- [x] Infant carrier protocol on Venice and boat gangways.

## Non-blocking

- [ ] Train minutes are windows, not a specific train number (intentional — still must verify Trenitalia).
- [ ] Ferry fares are bands; Navigazione Laghi PDFs change seasonally.
- [ ] Sigurtà 0–4 free ticket should be re-checked on sigurta.it the week of travel.
- [ ] Bardolino tourist medical hours are seasonal — confirm at the comune.
- [ ] Comparison table horizontal-scrolls on small phones (acceptable; first column sticky).
- [ ] Dark mode uses `color-mix`, which is fine in current browsers; very old WebViews may flatten the header blur.

## Trip-by-trip

### Venice (63, mandatory)

Timing: 07:15 leave, 07:40 park, ~1h28 train, hard leave 15:20, home 17:25. Buffer is real if they pick a direct train; a connection that lands at 15:50 in Venice would fail — the guide forbids that by making 15:20 a hard stop. Stroller honesty is correct. Driving to Tronchetto is correctly rejected.

### Ferry (88, mandatory)

Car stays home. Half-day shape. Wind cancellation path exists. Does not require Baia delle Sirene.

### Sigurtà / Borghetto (90)

Highest score. No beach (compensated by Peschiera + base days). Monday restaurant note present.

### Peschiera (84)

Beach without Sirmione. Explicitly not combinable with the Venice parking morning.

## UX

Hero states the product. Scores visible on cards. Filters, favorites, checklists, dark mode, print, mobile menu all present. Parking is a sand-colored card, not a footnote. Empty filter state exists.

## Honesty audit

Sirmione is rejected in copy, not quietly omitted. Venice score is not inflated. Gardaland is named as a trap. Rest days are scheduled. Official verify-tonight rule is repeated.

## Polish applied

- Print path opens all `details` via `beforeprint` / `afterprint`.
- Maps URLs print after links.
- Heart buttons hidden in print.
