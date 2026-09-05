# Execute pipeline

This is the one-click runbook. Follow it mechanically.

## Wave A — parallel research (launch together)

| Agent spec | Output |
| --- | --- |
| `agents/research_agent.md` | `shared/research_data.json` |
| `agents/local_expert_agent.md` | `shared/local_recommendations.json` |
| `agents/venice_agent.md` | `shared/venice_plan.json` |

Wait until all three files exist and parse as JSON.

Merge rule: if Local Expert names a place Research omitted, Scoring must still see it (Orchestrator may append a stub destination into research_data or instruct Scoring to union the lists).

## Wave B — scoring

| Agent spec | Output |
| --- | --- |
| `agents/scoring_agent.md` | `shared/scored_destinations.json` |

Confirm Venice is present and a ferry composite or ferry town is present.

## Wave C — itinerary + UX (parallel)

| Agent spec | Output |
| --- | --- |
| `agents/itinerary_agent.md` | `shared/itinerary.json` |
| `agents/ux_agent.md` | `shared/ui_spec.md` |

Confirm `trips.length === 4`.

## Wave D — frontend

| Agent spec | Output |
| --- | --- |
| `agents/frontend_agent.md` | `output/bardolino-trip-guide.html` |

Confirm the file has embedded `<style>` and `<script>` and no `cdn.` / `fonts.googleapis`.

## Wave E — QA

| Agent spec | Output |
| --- | --- |
| `agents/qa_agent.md` | `shared/qa_report.md` |

## Wave F — polish if needed

If verdict is FAIL or blocking items exist:

| Agent spec | Output |
| --- | --- |
| `agents/final_editor_agent.md` | patched HTML |

Then re-run QA once.

## Exit

Tell the human:

- Absolute path of the HTML
- The four trip titles
- Open instructions (offline file)
- Verify Trenitalia + Navigazione Laghi the night before
