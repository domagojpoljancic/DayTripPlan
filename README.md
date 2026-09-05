# Italy Trip Planner

> **Status:** Offline family guide in `output/bardolino-trip-guide.html` — **22 same-day loops**, real Wikimedia photos, Google Maps + official links for every place and parking lot, browse-first list, score tooltips, full agency guide pages. Pipeline JSON in `shared/` matches. Unzip, open in Cursor, or run `/generate-bardolino-guide`.

An autonomous multi-agent Cursor project that builds a **premium offline HTML travel guide** for a family staying in **Bardolino, Lake Garda, Italy**.

This is not a road-trip planner. The family keeps a fixed apartment in Bardolino. Every recommendation is a same-day excursion:

**Bardolino → Day Trip → Bardolino** (home before 18:00).

The user should not have to plan anything by hand.

---

## What this repo is

A Cursor-ready product team in a folder. Ten cooperating agents research, score, design, build, and QA a single-file website:

`output/bardolino-trip-guide.html`

Open that file on a laptop or phone. No internet. No build step. No framework.

---

## What works / stubbed / TBD

| Piece | Status | Notes |
| --- | --- | --- |
| Project architecture & agent specs | **Works** | Ten agents, schemas, prompts, Cursor command |
| One-click Cursor command `/generate-bardolino-guide` | **Works** | Orchestrator launches the full pipeline |
| Shared family + scoring rules | **Works** | Locked in `PLAN.md` and agent files |
| Sample pipeline outputs in `shared/` | **Works** | Research, local, Venice, scores, itinerary, UX, QA |
| Final offline HTML guide | **Works** | 22 trips; real local photos; Google Maps + official place/parking links; browse-first cards; city + lake filters; score tooltips |
| Live web preview (dev server) | **Works** | `./scripts/serve.sh` |
| Schema validator | **Works** | `python3 scripts/validate_pipeline.py` |
| Real-time ferry/train tickets | **TBD at travel time** | Guide tells you exactly which official sites to check the night before |
| Live weather | **TBD at travel time** | Offline weather *considerations* are included; live forecasts are not |

---

## The family (locked context)

- **Base:** Bardolino, Lake Garda, Italy
- **Stay:** 6 days
- **Car:** available every day
- **Baby:** under 6 months
- **Stroller:** yes
- **Evenings:** always back at the apartment
- **Priorities:** beaches, good food, easy walks, beautiful scenery, stress-free travel
- **Walking:** up to 1 hour is fine; no long hikes
- **Parking:** easy, close, realistic information is mandatory
- **Safety:** prefer secure towns

Mandatory trips (the system still decides *how*):

1. **Venice** (compare driving, park-outside, train, organized transport)
2. **Lake Garda boat/ferry day** (need not be a full day)

The rest of the menu is scored the same way. The family picks **5–6 loops** from about **22** same-day options.

---

## Quick start

### Option A — one click in Cursor (regenerate everything)

1. Open this folder in Cursor.
2. Run the command **`/generate-bardolino-guide`**.
3. Do nothing else. The orchestrator launches the agents, merges results, and writes the HTML.

Details: [`CURSOR_ONE_CLICK.md`](CURSOR_ONE_CLICK.md)

### Option B — open the already-generated guide

```bash
# macOS
open output/bardolino-trip-guide.html

# Linux
xdg-open output/bardolino-trip-guide.html
```

Open `output/bardolino-trip-guide.html` together with the `output/images/` folder (relative paths). Photos are local Wikimedia copies so the guide still works without a CDN. Google Maps and official site buttons need a network.

Or serve it locally:

```bash
./scripts/serve.sh
```

Then open the printed URL (default `http://127.0.0.1:47261/bardolino-trip-guide.html`).

### Validate pipeline JSON

```bash
python3 scripts/validate_pipeline.py
```

---

## Project map

```
.
├── README.md
├── CURSOR_ONE_CLICK.md      ← user-facing one-click instructions
├── AGENT_ORCHESTRATOR.md    ← how the team is run
├── CURSOR_RULES.md          ← hard constraints for every agent
├── ARCHITECTURE.md          ← data flow, dependencies, merge rules
├── PLAN.md                  ← locked trip rules + scoring
├── AGENTS.md                ← Cursor agent index
├── agents/                  ← one spec per agent
├── prompts/                 ← bootstrap / execute / review / improve
├── schemas/                 ← JSON contracts + HTML requirements
├── shared/                  ← agent outputs (the handshake layer)
├── output/                  ← HTML guide + local Wikimedia photos (`images/`)
├── scripts/                 ← validate, serve, fetch photos, inject media
└── .cursor/commands/        ← /generate-bardolino-guide
```

---

## Pipeline (what one click actually does)

1. Research, local-expert, and Venice agents run **in parallel**.
2. Results are merged into a destination pool.
3. Scoring agent ranks every candidate.
4. Itinerary architect locks a **menu of same-day loops** (at least four; the live guide is ~22 — they pick 5–6 in a 6-day stay).
5. UX designer writes the information architecture.
6. Frontend developer writes a single HTML file.
7. QA hunts unrealistic timing, parking lies, baby traps, and missing fields.
8. Final polish applies fixes.
9. `output/bardolino-trip-guide.html` is the deliverable.

---

## Quality bar

The guide must feel like a premium travel product (Apple / Airbnb / Google Travel / Lonely Planet), not like a chatbot dump of four famous places.

If a family cannot use it for the whole Bardolino stay without opening Google, it is not done.

---

## License

Private travel-planning project. Not affiliated with Navigazione Laghi, Trenitalia, or any destination.
