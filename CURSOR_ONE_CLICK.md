# One-click execution

The user performs **one action**. Cursor behaves as the product team.

## The action

In Cursor, open the command palette / chat slash menu and run:

```
/generate-bardolino-guide
```

That command is defined in:

`.cursor/commands/generate-bardolino-guide.md`

You do **not**:

- pick which agents to run
- paste prompts from this repo
- choose destinations
- edit HTML by hand
- coordinate merge order

The orchestrator does all of that.

---

## What happens after you hit enter

The active Cursor agent **becomes the Orchestrator**. It must:

1. Read `AGENT_ORCHESTRATOR.md`, `CURSOR_RULES.md`, `ARCHITECTURE.md`, and `PLAN.md`.
2. Launch agents 2–4 (Research, Local Expert, Venice) **in parallel** using Cursor Task/subagents.
3. Wait until `shared/research_data.json`, `shared/local_recommendations.json`, and `shared/venice_plan.json` exist and pass schema checks.
4. Launch the Scoring agent.
5. Launch the Itinerary Architect (depends on scores + Venice plan).
6. Launch the UX Designer in parallel with itinerary finalization if scores exist; otherwise after itinerary.
7. Launch the Frontend Developer with itinerary + UX spec.
8. Launch QA.
9. Launch Final Polish until QA blocking issues are gone.
10. Confirm `output/bardolino-trip-guide.html` exists, is a single file, and contains exactly four trips.

If any agent fails, the orchestrator retries that agent once with the review prompt, then continues. It does not stop to ask the user what to do.

---

## First-time setup (humans)

1. Unzip / clone this project.
2. Open the **project root** in Cursor (the folder that contains `README.md` and `.cursor/`).
3. Enable cloud/subagents if your Cursor build requires it (Task tool).
4. Run `/generate-bardolino-guide`.

No npm install. No API keys required for the offline HTML. Agents may use web search during generation; the **finished guide** must still work with the network off.

---

## If you are not in Cursor

You cannot fully regenerate AI research without an LLM. You can still:

```bash
python3 scripts/validate_pipeline.py
./scripts/serve.sh
```

and open the already-built guide in `output/`.

---

## Success criteria (orchestrator must not stop before these)

- [ ] Exactly 4 day trips, each Bardolino → destination → Bardolino
- [ ] Return target before 18:00 on every trip
- [ ] Venice is trip-present, with a compared transport decision
- [ ] One trip is a Lake Garda boat/ferry day
- [ ] The other two trips were selected from scored destinations, not from a fame list
- [ ] Every trip includes parking, stroller, baby, costs, maps link, rainy backup
- [ ] Output is `output/bardolino-trip-guide.html` — one file, embedded CSS/JS
- [ ] File opens offline, is mobile-first, printable, has dark mode
- [ ] QA report exists at `shared/qa_report.md`
