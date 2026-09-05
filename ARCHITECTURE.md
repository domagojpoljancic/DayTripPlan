# Architecture

## Mental model

This repo is a **directed acyclic pipeline** with a parallel fan-out at the start and a single HTML sink at the end.

```
                    ┌─────────────────────┐
                    │  family + PLAN.md   │
                    │  (locked context)   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   Research Agent      Local Expert Agent    Venice Specialist
   research_data.json  local_recommendations.json  venice_plan.json
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    Destination Scoring Agent
                    scored_destinations.json
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           Itinerary Architect      UX Designer
           itinerary.json           ui_spec.md
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    Frontend Developer
                    output/bardolino-trip-guide.html
                               │
                               ▼
                           QA Agent
                           qa_report.md
                               │
                               ▼
                      Final Polish Agent
                      output/bardolino-trip-guide.html
```

## Ownership (one writer per file)

| File | Writer | Readers |
| --- | --- | --- |
| `shared/research_data.json` | Research | Scoring, Itinerary, QA |
| `shared/local_recommendations.json` | Local Expert | Scoring, Itinerary, Frontend, QA |
| `shared/venice_plan.json` | Venice Specialist | Scoring, Itinerary, Frontend, QA |
| `shared/scored_destinations.json` | Scoring | Itinerary, UX, QA |
| `shared/itinerary.json` | Itinerary Architect | UX, Frontend, QA, Polish |
| `shared/ui_spec.md` | UX Designer | Frontend, QA, Polish |
| `output/bardolino-trip-guide.html` | Frontend, then Polish | QA, user |
| `shared/qa_report.md` | QA | Polish, Orchestrator |

No two agents write the same path at the same time except Polish, which is allowed to patch the HTML after QA.

## Orchestrator responsibilities

The Orchestrator does not research destinations and does not write CSS.

It:

- starts agents in the legal order
- runs the three research-family agents **in parallel**
- validates JSON against `schemas/`
- resolves conflicts (see below)
- refuses to launch Frontend until itinerary + UX spec exist
- refuses to declare done until QA has zero **blocking** issues
- writes `shared/pipeline_status.json` as a simple progress log (optional but recommended)

## Conflict resolution

When agents disagree, apply this stack in order:

1. **Hard constraints win.** 18:00 return, 2-hour drive cap, baby/stroller, Bardolino base.
2. **Venice transport** is owned by the Venice Specialist. Scoring may score Venice as a destination but must not override the chosen access mode.
3. **Local Expert** wins on hidden gems, food, and “don’t go there on Saturday.” Research wins on distances, parking lot names, and opening-hour sources.
4. **Scoring math** wins on which two non-mandatory trips make the final four. The Itinerary Architect may not sneak Sirmione in because “people expect it” if it lost the score.
5. **QA** wins on safety, unrealistic timing, and missing fields. Polish must apply QA blocking fixes.
6. **UX** wins on layout and hierarchy. Frontend may not invent new sections that contradict `ui_spec.md`, but may add small interaction details.

If two destinations tie within 2 points, prefer the one with the higher **parking + baby** subtotal.

## Data contracts

- Destinations: `schemas/destination.schema.json`
- Itinerary: `schemas/itinerary.schema.json`
- HTML: `schemas/html_requirements.md`

Agents must emit JSON that validates. Extra fields are allowed; missing required fields are not.

## Parallelism rules

**Legal in parallel**

- Research ∥ Local Expert ∥ Venice
- UX Designer ∥ Itinerary Architect (once scores exist; UX may use scores + PLAN if itinerary is still forming, then reconcile)
- Frontend must be sequential after itinerary + UX

**Illegal in parallel**

- Scoring before the three research files exist
- Itinerary before scores + Venice plan
- Frontend before itinerary
- Polish before QA

## Failure handling

| Failure | Orchestrator action |
| --- | --- |
| Agent produces invalid JSON | Re-run that agent with `prompts/review.md` + schema errors |
| Venice plan missing a comparison table | Re-run Venice agent only |
| Itinerary has ≠ 4 trips | Re-run Itinerary agent |
| HTML uses a CDN | Re-run Frontend with `html_requirements.md` |
| QA blocking > 0 | Polish, then QA again (max two QA loops) |
| Web search unavailable | Use conservative published ranges, mark `confidence: low`, still ship |

## Runtime (Cursor)

Agents are Cursor Task subagents (`subagent_type: generalPurpose` unless exploring files).

The slash command `/generate-bardolino-guide` is the process supervisor. See `agents/orchestrator.md`.
