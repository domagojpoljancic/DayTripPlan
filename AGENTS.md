# Agents

Cursor product team for the Bardolino family holiday guide.

The human runs **`/generate-bardolino-guide`**. The Orchestrator starts everyone else.

| Agent | Spec | Output |
| --- | --- | --- |
| Orchestrator | `agents/orchestrator.md` | pipeline coordination |
| Research | `agents/research_agent.md` | `shared/research_data.json` |
| Lake Garda local expert | `agents/local_expert_agent.md` | `shared/local_recommendations.json` |
| Venice specialist | `agents/venice_agent.md` | `shared/venice_plan.json` |
| Destination scoring | `agents/scoring_agent.md` | `shared/scored_destinations.json` |
| Itinerary architect | `agents/itinerary_agent.md` | `shared/itinerary.json` |
| UX designer | `agents/ux_agent.md` | `shared/ui_spec.md` |
| Frontend developer | `agents/frontend_agent.md` | `output/bardolino-trip-guide.html` |
| QA | `agents/qa_agent.md` | `shared/qa_report.md` |
| Final polish | `agents/final_editor_agent.md` | patched HTML |

Rules: `CURSOR_RULES.md` · Flow: `ARCHITECTURE.md` · Locked plan: `PLAN.md`
