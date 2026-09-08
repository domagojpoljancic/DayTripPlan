---
name: DayTripPlan Improvement Plan
overview: 'A prioritized, ticket-level plan to turn the Bardolino day-trip guide from a working browse-list into a premium, trustworthy, photo-led offline product, and to reconcile the multi-agent pipeline so the itinerary JSON becomes the single source of truth.'
todos:
  - id: T-06
    content: 'Reconcile product model to the menu (retire ''exactly 4'') across PLAN.md, CURSOR_RULES.md, ui_spec.md, frontend_agent.md, schemas'
    status: pending
  - id: T-01
    content: Make shared/itinerary.json the single source of truth; extend inject_guide_media.py to generate const TRIPS in the HTML
    status: pending
  - id: T-07
    content: 'Upgrade scripts/validate_pipeline.py: HTML↔itinerary parity, duplicate/missing image checks, forbidden-list parity'
    status: pending
  - id: T-05
    content: Replace duplicate/placeholder photos (bardolino-wine-oil/cavaion-wine/cisano-base) with real distinct credited images
    status: pending
  - id: T-02
    content: Add cross-trip comparison table + Compare view/nav
    status: pending
  - id: T-03
    content: Add favorites 'Saved' filter/view with empty state
    status: pending
  - id: T-04
    content: Show mandatory badge on cards + pinned Must-do rail for Venice/ferry
    status: pending
  - id: T-10
    content: 'Image pipeline: resize, WebP, srcset, width/height, lazy loading; target <~12MB'
    status: pending
  - id: T-09
    content: 'Design tokens refresh: semantic tokens, move off cream+terracotta cliché'
    status: pending
  - id: T-08
    content: 'Photo-led atmospheric hero with brand signal, no dashboard clutter'
    status: pending
  - id: T-12
    content: 'Card redesign: photo-led hierarchy, mandatory + parking severity badges'
    status: pending
  - id: T-11
    content: Typography hierarchy and tabular numerics
    status: pending
  - id: T-16
    content: Standardized parking honesty component from structured fields
    status: pending
  - id: T-17
    content: Scoring transparency component with bars + formula explainer
    status: pending
  - id: T-14
    content: 'Venice decision block upgrade (winner callout, rejected reasons, verify CTA)'
    status: pending
  - id: T-15
    content: Ferry go/no-go UX with land backup + verify link
    status: pending
  - id: T-18
    content: Add text search + Boat/Garden filter chips; document Close semantics
    status: pending
  - id: T-13
    content: 'Trip detail IA: section sub-nav + sticky Maps CTA'
    status: pending
  - id: T-20
    content: Mobile usability + tap-first score popover + sheet nav updates
    status: pending
  - id: T-21
    content: 'Offline/empty/error states (offline note, img onerror fallback, Saved/search empty)'
    status: pending
  - id: T-19
    content: 'Print scopes: this-trip / favorites / all'
    status: pending
  - id: T-22
    content: 'Intentional motion (max 3), reduced-motion safe'
    status: pending
  - id: T-23
    content: Base-day guidance content surfaced near menu
    status: pending
  - id: T-24
    content: 'Accessibility audit (AA contrast, non-color-only, focus)'
    status: pending
  - id: T-25
    content: Data freshness + consolidated verify-tonight block
    status: pending
  - id: T-26
    content: README / WIP honesty refresh to match generator + menu model
    status: pending
  - id: T-27
    content: Pipeline slimming decision documented in ARCHITECTURE.md/AGENTS.md
    status: pending
  - id: T-28
    content: Regenerate shared/qa_report.md for the menu product + validator automation
    status: pending
isProject: false
---
# DayTripPlan Improvement Plan

Audit of the private repo at `/workspace` (branch `main`, HEAD `036b48f`). The shipped product is [`output/bardolino-trip-guide.html`](output/bardolino-trip-guide.html) (943 lines, 164 KB, 22 trips) with local photos in `output/images/` (80 files, 71 MB). Everything below respects the locked family constraints (Bardolino base, same-day, home by 18:00, baby under 6 months, stroller, car, easy walks, parking honesty, Venice + ferry mandatory).

---

## 1. Executive audit

### Current strengths
- **Genuinely honest, agency-grade copy.** Trip text names lots, fill-times, ZTL traps, abort protocols, carrier-vs-stroller calls, and "why NOT" reasons. This is the product's real moat and must be protected.
- **Scoring is transparent and un-gamed.** The seven-weight formula (parking 20 / baby 20 / beauty 15 / food 15 / walking 10 / safety 10 / effort 10) is shown per trip; Venice sits at 63 and Sirmione at 64 on purpose, with rationale. Fame is explicitly rejected in copy.
- **Offline discipline holds.** No CDNs/webfonts/frameworks; embedded CSS/JS; local images; `file://`-safe; dark mode and print exist; `python3 scripts/validate_pipeline.py` passes.
- **Venice decision is real.** [`shared/venice_plan.json`](shared/venice_plan.json) compares 4 access modes with scored sub-criteria and a defensible winner (Peschiera train), surfaced as a table in the Venice detail.
- **Accessibility basics present.** Skip link, landmarks, `:focus-visible`, `prefers-reduced-motion`, `prefers-color-scheme`, 44px tap targets, aria on score controls.

### Critical weaknesses
- **Two sources of truth for trip data.** The HTML embeds a hand-authored `const TRIPS = [...]` (22 trips) that duplicates [`shared/itinerary.json`](shared/itinerary.json) (also 22 trips). They currently match by luck; nothing enforces it. `scripts/inject_guide_media.py` injects only PHOTOS/LINKS, not TRIPS. This is the biggest architectural risk and blocks cheaper models from editing safely.
- **Product-model contradiction across docs.** [`PLAN.md`](PLAN.md) and [`CURSOR_RULES.md`](CURSOR_RULES.md) say "exactly 4 trips"; the product ships a 22-trip menu; [`shared/ui_spec.md`](shared/ui_spec.md), [`agents/frontend_agent.md`](agents/frontend_agent.md), and [`shared/qa_report.md`](shared/qa_report.md) still describe the old 4-trip build. Weaker models will follow the wrong spec.
- **Required "comparison table of trips" is missing.** `schemas/html_requirements.md` and `ui_spec.md` require a cross-trip comparison table (and a "Compare" nav item). Only the Venice-modes table exists.
- **Favorites is a dead-end.** You can heart a trip and see a count, but there is no "Saved" filter/view to retrieve them.
- **Mandatory trips are invisible in browse.** Venice (63) and the ferry (88) carry a `mandatory` flag that never renders on cards; default sort is by score, so Venice lands near the bottom with no "must-do" signal.
- **Photo trust breach.** One identical 141 KB image is reused as `bardolino-wine-oil-1.jpg`, `bardolino-wine-oil-3.jpg`, `cavaion-wine-2.jpg`, and `cisano-base-1.jpg` (confirmed by md5). A guide about honesty is showing the same generic photo for four different places.
- **Design is a browse dashboard, not a premium product.** First viewport is text-on-flat-cream then a 2-column card grid — exactly the "dashboard clutter / sterile" pattern the taste brief forbids. The palette is literally the cream+terracotta lake cliché called out as a "Don't."
- **Image performance is poor for an offline phone artifact.** 71 MB total, single images up to 3.7 MB, no WebP, no `srcset`, no `width`/`height` (layout shift), and card/hero `<img>` lack `loading="lazy"` (22 card photos load eagerly).

### Biggest opportunity
Make [`shared/itinerary.json`](shared/itinerary.json) the single source of truth and generate the self-contained HTML from it (extending `inject_guide_media.py`), then spend the freed-up reliability budget on a photo-led hero, honest mandatory/parking signals, the missing comparison table, and an image pipeline. This converts a fragile hand-maintained file into a defensible product a cheaper model can extend ticket-by-ticket.

---

## 2. Product framing refresh

- **Who it's for:** Two parents with a baby under 6 months, staying 6 nights in one Bardolino apartment, car daily, deciding each morning where to go and how to survive it — offline, on a phone.
- **Core job-to-be-done:** "Tell me which same-day outing to do today, exactly where to park, when to leave to be home by 18:00, and what the baby needs — without opening Google."
- **What "done" means for vNext:**
  - A browseable **menu of ~18–22 same-day loops** (not four); the family picks 5–6 across 6 days. Venice and a Garda ferry day are mandatory and clearly flagged.
  - Trip data lives in `shared/itinerary.json`; the HTML is generated and self-contained.
  - Every trip has honest parking, real photos (no duplicates, credited), baby logistics, timing that returns before 18:00, and a rainy/abort backup.
  - The product looks and feels premium and photo-led on both mobile and desktop, offline.
- **Explicit non-goals:** overnight/road trips; anything returning after 18:00; long hikes or demanding sightseeing; live ticket/weather integration; accounts/backend; multi-family personalization; theme parks; a design language of endless stat strips, glow, or purple SaaS gradients.

---

## 3. Findings by area

- **F-01 — Architecture — Blocker.** Trip data is duplicated: inline `const TRIPS` in [`output/bardolino-trip-guide.html`](output/bardolino-trip-guide.html) vs [`shared/itinerary.json`](shared/itinerary.json). `inject_guide_media.py` regenerates only PHOTOS/LINKS. *Why it matters:* any edit risks divergence; cheaper models cannot know which to edit. *Direction:* itinerary.json becomes canonical; generator injects TRIPS; validator enforces parity.

- **F-02 — Architecture/Content — Blocker.** "Exactly 4 trips" in [`PLAN.md`](PLAN.md)/[`CURSOR_RULES.md`](CURSOR_RULES.md) contradicts the 22-trip product and the stale 4-trip [`shared/ui_spec.md`](shared/ui_spec.md), [`agents/frontend_agent.md`](agents/frontend_agent.md), [`shared/qa_report.md`](shared/qa_report.md). *Why:* contradictory instructions to future agents. *Direction:* adopt the menu model everywhere (Venice + ferry mandatory; pick 5–6).

- **F-03 — Functional — High.** Cross-trip comparison table required by `schemas/html_requirements.md` and `ui_spec.md` is absent (only Venice-modes table exists; no "Compare" nav). *Direction:* add a sortable/sticky comparison table of the menu.

- **F-04 — Functional — High.** Favorites cannot be viewed. `bardolino-favorites` is stored and counted but there is no "Saved" filter/view. *Direction:* add a Saved filter and make the header heart count open it.

- **F-05 — Functional/Content — High.** `mandatory` never renders on cards; Venice/ferry are not discoverable by a score-sorting user. *Direction:* mandatory badge on cards + a pinned "Must do" grouping regardless of sort.

- **F-06 — Content/Trust — Blocker.** Duplicate placeholder image reused across 4 trips (md5 `76eb783…`): `bardolino-wine-oil-1/3`, `cavaion-wine-2`, `cisano-base-1`. *Why:* destroys the honesty promise. *Direction:* replace with real, distinct, credited photos; validator rejects duplicate hashes.

- **F-07 — Performance/Offline/Mobile — High.** 71 MB images, up to 3.7 MB each; no WebP/`srcset`/dimensions; card+hero `<img>` not lazy. *Why:* slow first paint, layout shift, painful phone copy. *Direction:* resize+WebP pipeline, `width`/`height`, `loading="lazy"`, target < ~12 MB total.

- **F-08 — Design — High.** First viewport is a text hero on flat `--foam` then a 2-col grid — dashboard-y and sterile; palette is the cream+terracotta cliché the brief forbids. *Direction:* photo-led atmospheric hero + brand signal; evolve palette so deep lake ink/teal and real photography dominate, terracotta becomes a sparing accent.

- **F-09 — Design — Medium.** Typography leans on Palatino/system serif only; acceptable (no webfonts allowed) but under-expressed. *Direction:* deliberate type scale, tighter display leading, tabular numerics for scores/times, stronger eyebrow/kicker system.

- **F-10 — Design — Medium.** Cards carry four meta pills + score + description with weak hierarchy; parking word is a plain pill. *Direction:* redesign card so photo, name, score, and one decisive line (parking + leave→home) lead; demote the rest.

- **F-11 — Content/Trust — High.** Parking honesty exists but is unstructured prose per trip; no consistent lot/cost/fill-time/backup/ZTL component, and no explicit "verify tonight" affordance tied to official links. *Direction:* standardized parking component fed by structured fields.

- **F-12 — Functional — Medium.** Venice decision is strong in data but the detail table is plain and the "why others lost" reasons from `venice_plan.json` are not fully surfaced. *Direction:* upgrade the decision block (winner callout, rejected reasons, verify-Trenitalia CTA).

- **F-13 — Functional — Medium.** Ferry day depends on wind; the copy says "decide by 09:00" but there is no prominent go/no-go + land-backup affordance. *Direction:* ferry go/no-go callout linking the land backup (`torri-car`) and Navigazione Laghi verify link.

- **F-14 — Design/Functional — Medium.** Scoring is transparent numerically but visually flat (list of numbers). *Direction:* lightweight bars, consistent breakdown component in card popover + detail, one-line formula explainer.

- **F-15 — Functional — Medium.** With 22 trips there is no text search; filters lack `boat`/`garden` chips though tags exist; `close` silently excludes cities. *Direction:* add search, add missing filter chips, document filter semantics.

- **F-16 — Performance — Medium.** Print renders all 22 full guides every load via `renderPrint()`; no "print this trip"/"print favorites". *Direction:* print scopes (current trip / favorites / all) and lazier print DOM.

- **F-17 — Mobile — Medium.** Two sticky bars stack (`header.top` + `#detail-bar`); score popover is hover/focus/click; long detail pages lack in-page section nav. *Direction:* verify sticky offsets, make popover tap-first on touch, add detail sub-nav + sticky "Maps" CTA.

- **F-18 — Offline/Empty states — Medium.** Maps/official buttons silently fail offline; no image error fallback (SVG covers exist but only when zero photos); filter-empty exists, favorites-empty does not. *Direction:* offline note on external buttons, `onerror` image fallback, empty states for Saved.

- **F-19 — Architecture/DX — Medium.** Validator checks `shared/` JSON and forbidden strings but not HTML↔itinerary parity, duplicate images, image existence, or full forbidden-list parity with `html_requirements.md` (misses `react`, `fonts.gstatic`). *Direction:* extend `scripts/validate_pipeline.py`.

- **F-20 — Architecture — Low/Medium (decision).** Ten agent specs, prompts, schemas for a single hand-authored HTML is heavy relative to output. *Why:* maintenance overhead, drift risk (F-02). *Direction:* keep the pipeline as the narrative/generation contract but slim to the roles that actually produce artifacts, and wire them to the generator so specs match reality.

- **F-21 — Content — Low.** Data freshness: `generated_at` timestamps and "verify night before" notes are scattered. *Direction:* a single freshness/verify block + per-trip `confidence` surfaced.

- **F-22 — Content — Low.** README status banner is accurate but should keep a clear WIP signal and be re-synced after the menu-model change.

- **F-23 — Accessibility — Low/Medium.** Verify contrast of `--ink-soft`/`--gold` on `--foam`, color-only "winner" row in tables, popover focus trap, and that new components keep numeric (not color-only) meaning.

---

## 4. Target experience

- **First 10 seconds (mobile & desktop):** A full-bleed, credited photo of Lake Garda from the Bardolino shore with a restrained wordmark and one promise line ("Same apartment. A menu of days. Home before dinner."), plus the four family-fact chips. One clear scroll cue. No toolbar, no grid, no stat soup above the fold.
- **Browse flow:** Below the hero, a "Must do" rail (Venice + ferry, flagged mandatory) then the scored menu as photo-led cards. Filters (All / Lake / Beach / Food / Easy / Close / City / Boat / Garden), sort, search, and a Saved toggle. Each card leads with photo → name → score → one decisive line (parking + leave→home). Empty and Saved states are designed.
- **Trip decision flow:** Opening a trip shows a photo gallery, an at-a-glance strip, a scannable hour-by-hour timeline, a standardized parking card (lot, cost, fill-time, backup, ZTL, Maps + official links, verify note), baby logistics, costs, and a rainy/abort backup. Venice adds the mode-comparison decision block; the ferry adds a go/no-go callout. A cross-trip Compare view lets parents line up candidates on score, parking, drive, return, stroller, beach, food.
- **Day-of-use flow:** On the phone, offline: the address/lot text is always visible even when Maps fails; "verify tonight" links are grouped; print/export produces this-trip or favorites as a clean PDF; checklists persist.

---

## 5. Design system proposal

- **Visual direction:** Photography-led, calm, editorial-but-warm travel product. Real Garda imagery dominates; UI chrome recedes. Distinct from cream+terracotta cliché: lean into deep lake ink/teal as the dominant surface accent and let photos carry warmth; terracotta only for small emphasis (mandatory, alerts, active).
- **Type hierarchy (system fonts only):** Display serif (Palatino/Georgia stack) for wordmark + trip titles at a tighter leading and larger clamp; sans (system-ui) for everything else. Scale roughly: Display clamp(2.2–3rem); H2 1.75rem; H3 1.25rem; body 1rem; kicker 0.75rem uppercase tracked. Tabular numerics for scores, times, costs.
- **Color tokens (extend existing `:root`/dark):** keep `--ink`, `--water`, `--foam`, `--sand`, `--terra`, `--gold`; add semantic tokens: `--surface`, `--surface-2`, `--accent` (=water), `--alert` (=terra), `--must` (mandatory), `--ok`, `--warn`, `--scrim` (hero photo overlay). Reduce raw `--foam` flat backgrounds in favor of photo + scrim and `--surface` cards. All pairs must meet WCAG AA.
- **Component rules:** Cards only where they aid a decision (menu, comparison, parking, checklist). One job per section. Buttons: one primary per context; Maps = primary, official = ghost. Badges: mandatory (`--must`), parking severity (easy/moderate/hard/severe with text, not color-only).
- **Layout rules:** 1120px max content; hero full-bleed; 2-col card grid desktop → 1-col ≤860px; generous vertical rhythm (24–40px section gaps); avoid pill strips longer than one row.
- **Motion rules (max 3, intentional, respect reduced-motion):** (1) hero photo subtle scale/parallax on load only; (2) card image zoom on hover/focus; (3) detail open cross-fade/scroll-to-top. Nothing else animates.
- **Do:** photo-first, honest badges, tabular numbers, calm spacing, offline-visible text. **Don't:** purple SaaS gradients, glow soup, emoji clutter, broadsheet columns, endless stat strips, decorative motion.

---

## 6. Prioritized roadmap

### P0 (must fix before more features)
- F-01 single source of truth + generator (T-01)
- F-02 doc/model reconciliation (T-06)
- F-06 duplicate/placeholder photos (T-05)
- F-03 comparison table (T-02)
- F-04 favorites view (T-03)
- F-05 mandatory visibility (T-04)
- F-19 validator upgrades (T-07)

### P1 (high leverage)
- F-07/F-10 image pipeline + card redesign (T-10, T-12)
- F-08/F-09 hero + design tokens + type (T-08, T-09, T-11)
- F-11 parking component (T-16)
- F-12/F-13 Venice + ferry UX (T-14, T-15)
- F-14 scoring transparency (T-17)
- F-15 search/filters (T-18)
- F-17 mobile + detail nav (T-20)
- F-18 offline/empty states (T-21)

### P2 (polish / later)
- F-16 print scopes (T-19)
- motion (T-22)
- base-day content (T-23)
- accessibility audit (T-24)
- data freshness (T-25)
- README/WIP (T-26)
- pipeline slimming (T-27)
- QA regen (T-28)

---

## 7. Execution tickets

### T-01 — Make itinerary.json the single source of truth (generate TRIPS)
- **Priority:** P0
- **Goal:** HTML trip data is generated from `shared/itinerary.json`, not hand-maintained inline.
- **Context:** F-01. Today `const TRIPS` in the HTML duplicates the JSON; `inject_guide_media.py` injects only PHOTOS/LINKS.
- **Implementation notes:** Extend [`scripts/inject_guide_media.py`](scripts/inject_guide_media.py) to read `shared/itinerary.json`, map fields to the HTML trip shape, and replace the `const TRIPS = [...]` block between stable anchors (mirror the PHOTOS/LINKS slice approach). Add a mapping layer so JSON field names (`why_selected`, `transport.*`, `experience.*`, `family.*`) drive the HTML keys (`why`, `getting`, `there`, `babyNotes`). Keep the output a single offline file (build-time codegen only; opening needs no build).
- **Acceptance criteria:**
  - [ ] Editing a trip in `shared/itinerary.json` and running the generator updates the HTML with no manual HTML edit.
  - [ ] Generated HTML still passes `scripts/validate_pipeline.py` and opens offline via `file://`.
  - [ ] No `const TRIPS` literal remains hand-authored (it is emitted by the script).
- **Test plan:** Change one trip's `expected_return` in JSON, regenerate, confirm HTML card + detail reflect it; diff shows only intended change.
- **Out of scope:** Changing trip content; redesigning UI.
- **Depends on:** none.

### T-02 — Cross-trip comparison table + Compare view
- **Priority:** P0
- **Goal:** Add the required comparison table of the menu.
- **Context:** F-03; required by `schemas/html_requirements.md` and `ui_spec.md`.
- **Implementation notes:** New section + nav item "Compare" in [`output/bardolino-trip-guide.html`](output/bardolino-trip-guide.html). Reuse `.table-scroll`/`table.cmp` styles. Columns: Name, Score, Leave, Return, Drive, Parking, Stroller, Beach, Food highlight, Difficulty. Sticky first column on mobile; honor current filter/sort; row click opens the trip.
- **Acceptance criteria:**
  - [ ] Comparison table lists all filtered trips with the columns above.
  - [ ] Sticky first column + horizontal scroll works ≤480px.
  - [ ] "Compare" reachable from desktop nav and mobile sheet.
- **Test plan:** Filter to Lake, confirm table matches cards; mobile scroll; row → detail.
- **Out of scope:** New scoring columns.
- **Depends on:** T-01 (reads generated data).

### T-03 — Favorites view ("Saved" filter)
- **Priority:** P0
- **Goal:** Let users retrieve hearted trips.
- **Context:** F-04.
- **Implementation notes:** Add a "Saved" filter chip and make header `#fav-count` toggle it. Extend `matchesFilter` for `saved` (id in `favs`). Add favorites-empty state ("No saved trips yet — tap the heart on any day.").
- **Acceptance criteria:**
  - [ ] Saved filter shows only hearted trips and updates live on heart toggle.
  - [ ] Empty state renders when none saved.
  - [ ] Works in private mode (in-memory) without throwing.
- **Test plan:** Save 3 trips, filter Saved, unsave one, confirm list + count update.
- **Out of scope:** Cross-device sync.
- **Depends on:** T-01.

### T-04 — Mandatory visibility (badge + pinned rail)
- **Priority:** P0
- **Goal:** Venice and ferry are always discoverable and marked must-do.
- **Context:** F-05.
- **Implementation notes:** Render a `--must` badge on cards where `trip.mandatory`. Add a "Must do" rail above the menu showing the two mandatory trips regardless of sort/filter (with a note that Venice scores low on comfort by design).
- **Acceptance criteria:**
  - [ ] Mandatory badge visible on Venice + ferry cards and details.
  - [ ] Must-do rail persists across sort/filter (except when a filter explicitly excludes them, still reachable via rail).
- **Test plan:** Sort by score; confirm Venice still pinned in rail with badge.
- **Out of scope:** Changing scores.
- **Depends on:** T-01.

### T-05 — Replace duplicate/placeholder photos
- **Priority:** P0
- **Goal:** Every trip shows real, distinct, credited images.
- **Context:** F-06 (md5 `76eb783…` reused 4×).
- **Implementation notes:** Re-run/patch [`scripts/fetch_trip_photos.py`](scripts/fetch_trip_photos.py) for `bardolino-wine-oil`, `cavaion-wine`, `cisano-base` (and audit all); ensure `output/images/catalog.json` credits are correct; remove the reused generic file. Keep `SKIP_FILES` logic; add a dedupe guard by content hash during collection.
- **Acceptance criteria:**
  - [ ] No two image files in `output/images/` share an md5 hash.
  - [ ] Each trip's photos visually match that place (spot-check credits/titles).
  - [ ] Credits render and are ≤90 chars.
- **Test plan:** `md5sum` uniqueness check; open affected trips; verify captions.
- **Out of scope:** Art direction/resizing (T-10).
- **Depends on:** none (can parallel T-01).

### T-06 — Reconcile product model to the menu (retire "exactly 4")
- **Priority:** P0
- **Goal:** All docs describe the ~18–22 menu with Venice + ferry mandatory.
- **Context:** F-02.
- **Implementation notes:** Update [`PLAN.md`](PLAN.md), [`CURSOR_RULES.md`](CURSOR_RULES.md) rule 17, [`shared/ui_spec.md`](shared/ui_spec.md) (4-trip language on lines 7/38/44/49/51), [`agents/frontend_agent.md`](agents/frontend_agent.md) ("do not invent a fifth trip"), [`schemas/itinerary.schema.json`](schemas/itinerary.schema.json) intent note, and [`schemas/html_requirements.md`](schemas/html_requirements.md). Define canonical: menu of same-day loops; Venice + Garda ferry mandatory; family picks 5–6; two base/nap days acknowledged.
- **Acceptance criteria:**
  - [ ] No doc asserts "exactly four" as the product model.
  - [ ] ui_spec/frontend_agent/qa expectations match the shipped menu.
  - [ ] README status remains accurate (see T-26).
- **Test plan:** Grep for "four"/"exactly 4"/"fifth trip" returns only historical/context mentions.
- **Out of scope:** Rewriting scoring weights.
- **Depends on:** none.

### T-07 — Validator upgrades (parity, dedupe, forbidden parity)
- **Priority:** P0
- **Goal:** Automated guards for the new invariants.
- **Context:** F-19.
- **Implementation notes:** Extend [`scripts/validate_pipeline.py`](scripts/validate_pipeline.py): (a) parse `const TRIPS`/generated data and assert HTML trip ids == `shared/itinerary.json` ids; (b) fail on duplicate image md5; (c) fail if a referenced `images/*` file is missing; (d) align `FORBIDDEN_HTML` with `html_requirements.md` (add `react`, `fonts.gstatic`, `unpkg`, keep existing); (e) warn if any mandatory trip missing.
- **Acceptance criteria:**
  - [ ] Validator fails when HTML and itinerary ids diverge.
  - [ ] Validator fails on duplicate or missing images.
  - [ ] Existing PASS still holds after T-01/T-05.
- **Test plan:** Introduce a divergence and a dup image; confirm FAIL; revert; confirm PASS.
- **Out of scope:** Full JSON-schema validation library.
- **Depends on:** T-01, T-05.

### T-08 — Photo-led atmospheric hero
- **Priority:** P1
- **Goal:** Premium first viewport, brand signal, no dashboard clutter.
- **Context:** F-08; taste brief.
- **Implementation notes:** Full-bleed credited Garda/Bardolino photo with `--scrim` overlay, wordmark, one promise line, four fact chips, scroll cue. Toolbar/grid moved below the fold. Keep offline (local image) + reduced-motion.
- **Acceptance criteria:**
  - [ ] Above-the-fold shows photo + wordmark + one line + chips only.
  - [ ] AA contrast of hero text over scrim (light + dark).
  - [ ] No layout shift; hero image has dimensions + eager decode.
- **Test plan:** Mobile (390px) and desktop (1440px) screenshots; Lighthouse CLS ~0.
- **Out of scope:** Video/parallax libraries.
- **Depends on:** T-09, T-10.

### T-09 — Design tokens refresh (de-cliché palette)
- **Priority:** P1
- **Goal:** Stronger brand, move off cream+terracotta cliché.
- **Context:** F-08.
- **Implementation notes:** In the `:root`/dark blocks of the HTML (and mirror in `ui_spec.md`), introduce semantic tokens (`--surface`, `--surface-2`, `--accent`, `--alert`, `--must`, `--scrim`), reduce flat `--foam` fields, make ink/teal dominant, terracotta an accent. Keep names backward compatible.
- **Acceptance criteria:**
  - [ ] All components reference semantic tokens; no new hard-coded hexes in components.
  - [ ] Light/dark both AA; visual regression reviewed.
- **Test plan:** Toggle theme across hero/cards/detail/table; contrast checks.
- **Out of scope:** New fonts (none allowed).
- **Depends on:** none (precedes T-08/T-12).

### T-10 — Image pipeline (resize, WebP, srcset, dims, lazy)
- **Priority:** P1
- **Goal:** Fast, phone-friendly offline images.
- **Context:** F-07.
- **Implementation notes:** Add a resize/encode step (in `fetch_trip_photos.py` or a new `scripts/optimize_images.py`): produce WebP at card (~800px) and hero (~1600px) widths, keep a JPG fallback, write `width`/`height` into `catalog.json`, and have `inject_guide_media.py` emit `<img>` with dimensions, `srcset`, and `loading="lazy"` (hero eager). Target total < ~12 MB.
- **Acceptance criteria:**
  - [ ] No single image > ~400 KB; total `output/images/` < ~15 MB.
  - [ ] Every `<img>` has `width`, `height`; non-hero images lazy.
  - [ ] Offline `file://` still renders all images.
- **Test plan:** `du -sh output/images`; Lighthouse mobile; offline check with network disabled.
- **Out of scope:** CDN/hosting.
- **Depends on:** T-05.

### T-11 — Typography hierarchy
- **Priority:** P1
- **Goal:** Expressive, scannable type within system fonts.
- **Context:** F-09.
- **Implementation notes:** Tune `--fs-*` scale, display leading, letter-spacing on kickers, tabular-nums for scores/times/costs; ensure trip titles use the serif at a confident size.
- **Acceptance criteria:**
  - [ ] Clear 4-level hierarchy (display/H2/H3/body) visible in hero, card, detail.
  - [ ] Numeric alignment in scores/timeline/costs.
- **Test plan:** Visual review mobile+desktop.
- **Out of scope:** Webfonts.
- **Depends on:** T-09.

### T-12 — Card redesign (hierarchy + signals)
- **Priority:** P1
- **Goal:** Photo-led card that leads with the decision.
- **Context:** F-10, F-05.
- **Implementation notes:** Reorder to photo → name + score → one decisive line (parking word + leave→home + drive) → save; demote extra pills. Add mandatory + parking-severity badges. Keep whole-card click + separate Save/Open targets.
- **Acceptance criteria:**
  - [ ] Card readable in < 2s: what/where/how-hard/when.
  - [ ] Mandatory + parking severity visible; description not hidden (per html_requirements).
  - [ ] Tap targets ≥44px; hover/focus image zoom (reduced-motion safe).
- **Test plan:** Mobile grid → 1-col; keyboard nav; screenshot review.
- **Out of scope:** New data fields.
- **Depends on:** T-01, T-09, T-10.

### T-13 — Trip detail information architecture
- **Priority:** P1
- **Goal:** Scannable, navigable detail pages.
- **Context:** F-17.
- **Implementation notes:** Add in-detail sub-nav (Timeline · Getting there · Once there · Baby · Costs · Backup) and a sticky "Maps" CTA for the open trip. Preserve existing sections/order.
- **Acceptance criteria:**
  - [ ] Sub-nav jumps to sections; sticky Maps CTA opens the trip's Maps URL.
  - [ ] Two sticky bars don't overlap content on mobile.
- **Test plan:** Open Venice/ferry on mobile; verify anchors + sticky offsets.
- **Out of scope:** Routing/history rework.
- **Depends on:** T-01.

### T-14 — Venice decision block upgrade
- **Priority:** P1
- **Goal:** Make the "why this way in" decision unmistakable.
- **Context:** F-12; data in [`shared/venice_plan.json`](shared/venice_plan.json).
- **Implementation notes:** Winner callout, all four modes with verdicts, surfaced rejected reasons, and a prominent "Verify Trenitalia tonight" link. Style the winner row beyond color-only.
- **Acceptance criteria:**
  - [ ] Winner + 3 rejected modes with one-line reasons visible.
  - [ ] Verify-Trenitalia CTA present; winner indicated non-color-only.
- **Test plan:** Venice detail review mobile+desktop; print includes table.
- **Out of scope:** Live train data.
- **Depends on:** T-01.

### T-15 — Ferry go/no-go UX
- **Priority:** P1
- **Goal:** Wind decision + land backup are obvious.
- **Context:** F-13.
- **Implementation notes:** Add a go/no-go callout to `garda-ferry` linking the land backup (`torri-car`) and the Navigazione Laghi verify link, with the "decide by 09:00" rule elevated.
- **Acceptance criteria:**
  - [ ] Callout states go/no-go rule, backup link, and verify link.
- **Test plan:** Ferry detail review; backup link opens `torri-car`.
- **Out of scope:** Live weather.
- **Depends on:** T-01, T-13.

### T-16 — Standardized parking component
- **Priority:** P1
- **Goal:** Consistent, honest parking block everywhere.
- **Context:** F-11.
- **Implementation notes:** Render a single parking card from structured fields (lot, cost, difficulty, fill-time, backup, ZTL, Maps + official links, verify note). Ensure `shared/itinerary.json` `transport`/parking fields feed it; keep address/lot as visible text (offline).
- **Acceptance criteria:**
  - [ ] Every trip shows the same parking structure with all fields.
  - [ ] Lot name/address visible as text even if Maps fails offline.
  - [ ] Parking severity badge matches copy.
- **Test plan:** Spot-check Sirmione (severe), Peschiera (moderate), ferry (easy).
- **Out of scope:** Live space availability.
- **Depends on:** T-01.

### T-17 — Scoring transparency component
- **Priority:** P1
- **Goal:** Make the seven-weight math legible.
- **Context:** F-14.
- **Implementation notes:** Reusable breakdown with lightweight bars + weights in card popover and detail; one-line formula explainer; keep numeric text (not color-only). Reuse across popover/detail/comparison.
- **Acceptance criteria:**
  - [ ] Breakdown shows each criterion, weight, value, and rationale.
  - [ ] Bars have numeric labels; AA contrast.
- **Test plan:** Compare Sigurtà (90) vs Venice (63) breakdowns.
- **Out of scope:** Changing weights/scores.
- **Depends on:** T-01.

### T-18 — Search + filter/sort completeness
- **Priority:** P1
- **Goal:** Findability across 22 trips.
- **Context:** F-15.
- **Implementation notes:** Add a text search (name/short/tags), add `Boat` and `Garden` filter chips, document `Close` semantics (≤20 min, excludes city). Keep filters/sort/search composable.
- **Acceptance criteria:**
  - [ ] Search narrows cards + comparison live; clearable.
  - [ ] Boat/Garden chips filter correctly; empty state respected.
- **Test plan:** Search "wine"/"venice"; toggle Boat; combine with sort.
- **Out of scope:** Fuzzy search library.
- **Depends on:** T-01, T-02.

### T-19 — Print scopes
- **Priority:** P2
- **Goal:** Useful PDFs without 22 full guides by default.
- **Context:** F-16.
- **Implementation notes:** Print options: current trip, favorites, or all; build print DOM on demand instead of always rendering all via `renderPrint()`.
- **Acceptance criteria:**
  - [ ] "Print this trip" outputs one trip + pack/practical.
  - [ ] "Print favorites" outputs saved trips.
  - [ ] Details expand in print; maps URLs shown as text.
- **Test plan:** Print-to-PDF each scope; verify page breaks.
- **Out of scope:** Server-side PDF.
- **Depends on:** T-03.

### T-20 — Mobile usability + popover behavior
- **Priority:** P1
- **Goal:** Smooth touch experience.
- **Context:** F-17.
- **Implementation notes:** Verify sticky offsets (`header.top` + `#detail-bar`), make score popover tap-first on touch (avoid hover-only), ensure sheet nav includes new items (Compare/Saved), maintain 44px targets.
- **Acceptance criteria:**
  - [ ] Popover opens/closes reliably by tap; closes on outside tap.
  - [ ] No content hidden behind sticky bars on iOS Safari widths.
- **Test plan:** 360/390/414px manual checks; keyboard + screen-reader smoke.
- **Out of scope:** Native app behaviors.
- **Depends on:** T-13, T-17.

### T-21 — Offline / empty / error states
- **Priority:** P1
- **Goal:** Graceful degradation.
- **Context:** F-18.
- **Implementation notes:** Add a subtle "needs data" hint near Maps/official buttons; `<img onerror>` fallback to the existing `coverSvg`; favorites-empty and search-empty states; confirm localStorage failures are caught (already partly handled).
- **Acceptance criteria:**
  - [ ] With network off, addresses/lots remain usable; broken image → SVG cover.
  - [ ] Saved/search empty states render.
- **Test plan:** Disable network; rename an image to force error; verify fallback.
- **Out of scope:** Service worker (forbidden).
- **Depends on:** T-03, T-18-adjacent.

### T-22 — Intentional motion (max 3)
- **Priority:** P2
- **Goal:** Tasteful motion, reduced-motion safe.
- **Context:** design brief.
- **Implementation notes:** Hero load scale; card image hover/focus zoom; detail open cross-fade. Nothing else; all gated by `prefers-reduced-motion`.
- **Acceptance criteria:**
  - [ ] Exactly the three motions; disabled under reduced-motion.
- **Test plan:** Toggle OS reduced-motion; verify no animation.
- **Out of scope:** Scroll-jacking.
- **Depends on:** T-08, T-12.

### T-23 — Base-day guidance content
- **Priority:** P2
- **Goal:** Acknowledge the 2 nap/beach days explicitly.
- **Context:** PLAN base-day expectation; F-21.
- **Implementation notes:** Ensure the "six-day shape" note and base-day framing are prominent (already present in practical notes); tie `cisano-base`/`bardolino-wine-oil` as base-day picks.
- **Acceptance criteria:**
  - [ ] A clear base-day explanation exists near the menu, not buried.
- **Test plan:** Content review.
- **Out of scope:** New trips.
- **Depends on:** T-06.

### T-24 — Accessibility audit
- **Priority:** P2
- **Goal:** Confirm AA + non-color-only meaning.
- **Context:** F-23.
- **Implementation notes:** Contrast pass on new tokens, table winner indicator, badges, popover focus management, alt text from `catalog.json`.
- **Acceptance criteria:**
  - [ ] All text ≥ AA; interactive elements keyboard reachable; no color-only signals.
- **Test plan:** axe/Lighthouse a11y; keyboard-only walkthrough.
- **Out of scope:** WCAG AAA.
- **Depends on:** T-08–T-17.

### T-25 — Data freshness + verify consolidation
- **Priority:** P2
- **Goal:** One place to see freshness + verify actions.
- **Context:** F-21.
- **Implementation notes:** Surface `generated_at` and a consolidated "verify tonight" list (Trenitalia, Navigazione Laghi, Sigurtà tickets, comune medical hours); optionally show per-trip `confidence`.
- **Acceptance criteria:**
  - [ ] Freshness date visible; verify list complete and linked.
- **Test plan:** Footer/practical review.
- **Out of scope:** Live feeds.
- **Depends on:** T-01.

### T-26 — README / WIP honesty refresh
- **Priority:** P2
- **Goal:** README matches reality post-changes with a clear WIP banner and accurate status/quick-start.
- **Context:** F-22; user rule to refresh README before pushes.
- **Implementation notes:** Update [`README.md`](README.md) status table (works/stubbed/TBD), the menu model, generator command (T-01), image pipeline, and quick-start; keep the WIP signal.
- **Acceptance criteria:**
  - [ ] README reflects generator flow, menu model, and current features.
  - [ ] Quick-start commands verified.
- **Test plan:** Follow README from clean checkout; commands work.
- **Out of scope:** Marketing copy.
- **Depends on:** T-01, T-06, T-10.

### T-27 — Pipeline slimming decision (doc)
- **Priority:** P2
- **Goal:** Right-size the agent pipeline to what produces artifacts.
- **Context:** F-20.
- **Implementation notes:** In [`ARCHITECTURE.md`](ARCHITECTURE.md)/[`AGENTS.md`](AGENTS.md), mark which agents generate real files vs narrative; wire frontend agent output to the generator (T-01); note that itinerary.json is canonical. Do not delete specs; clarify roles.
- **Acceptance criteria:**
  - [ ] Docs state the source of truth and the generation path.
  - [ ] No agent spec instructs hand-editing `const TRIPS`.
- **Test plan:** Doc review against actual scripts.
- **Out of scope:** Removing the pipeline.
- **Depends on:** T-01, T-06.

### T-28 — Regenerate QA report + QA automation
- **Priority:** P2
- **Goal:** QA reflects the menu product and new invariants.
- **Context:** F-02; stale [`shared/qa_report.md`](shared/qa_report.md).
- **Implementation notes:** Rewrite qa_report for the 22-trip menu; add the validator checks (T-07) as the automated portion; keep the honesty audit.
- **Acceptance criteria:**
  - [ ] qa_report matches shipped product; validator PASS documented.
- **Test plan:** Run validator; cross-check report claims.
- **Out of scope:** New tooling frameworks.
- **Depends on:** T-07.

---

## 8. Suggested delivery sequence

- **Phase 1 — Truth & core function (P0).** T-06 (docs) → T-01 (generator) → T-07 (validator) → T-05 (photos) → T-02, T-03, T-04. Checkpoint: validator PASS, HTML↔itinerary parity, no duplicate images, comparison table + favorites view + mandatory badges live, offline verified. One PR per ticket; merge behind validator.
- **Phase 2 — Design & trust (P1).** T-09 → T-10 → T-11 → T-08 → T-12 → T-16 → T-17 → T-14 → T-15 → T-18 → T-13 → T-20 → T-21. Checkpoint: mobile + desktop screenshots, Lighthouse (perf/a11y/CLS), offline check, honesty spot-audit on 5 trips.
- **Phase 3 — Polish (P2).** T-19 → T-22 → T-23 → T-24 → T-25 → T-27 → T-26 → T-28. Checkpoint: full QA matrix (section 9) green; README refreshed before push.

Merge/verification at each checkpoint: run `python3 scripts/validate_pipeline.py`, open the HTML with network disabled, and review mobile (≤414px) + desktop.

---

## 9. QA matrix

- **Family constraints:** every trip returns before 18:00; drive ≤ ~2h one way; walking ≤ ~1h; no long hikes; Venice + ferry present and mandatory-flagged; base/nap days acknowledged.
- **Parking honesty:** each trip names lot(s), cost band, difficulty, fill-time, backup, ZTL; lot/address visible as text offline; official/operator link present; no "parking available" hand-waving.
- **Timing feasibility:** timelines start ≥ leave and end ≤ home; Venice hard-leave 15:20 preserved; ferry go/no-go + land backup present.
- **Mobile:** cards/comparison usable ≤414px; sticky bars don't occlude; popover tap works; 44px targets.
- **Offline:** full render via `file://` network-off; Maps/official buttons degrade gracefully; images present and lazy; total image weight within budget.
- **Print:** this-trip / favorites / all scopes; details expand; maps URLs as text; sane page breaks.
- **Dark mode:** all components AA in dark; header blur acceptable; winner/badges not color-only.
- **Content accuracy:** no duplicate images; credits correct; no lorem/"welcome"/AI phrasing; scores un-inflated; Venice/Sirmione honesty intact.
- **Pipeline integrity:** HTML ids == itinerary ids; validator PASS; docs describe generator + menu model.

---

## 10. Open questions

- **Source-of-truth (recommended default: itinerary.json + generator).** If the HTML and pipeline conflict, `shared/itinerary.json` should win and the HTML should be generated from it (T-01), because it makes the product editable by weaker models and re-aligns the pipeline. Proceed with this unless the maintainer wants the HTML to stay hand-authored (then drop T-01/T-07 parity and instead delete the pipeline claims).
- **Image sourcing for T-05/T-10.** Default: continue Wikimedia (CC) via `fetch_trip_photos.py` with dedupe + resize. Confirm if any licensing constraint prevents WebP re-encoding of CC images (attribution retained either way).
- **Palette direction (T-09).** Default: keep the existing token names but shift dominance to ink/teal + photography with terracotta as accent. Confirm if the maintainer wants a bolder repalette vs a restrained de-cliché.
- **Menu size (T-06).** Default: keep ~22 and market "pick 5–6." Confirm if the menu should be trimmed for focus.
