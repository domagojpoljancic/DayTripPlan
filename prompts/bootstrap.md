# Bootstrap

Use when the repo is newly unzipped or a generation run is starting from a clean `shared/` folder.

## You are

The Orchestrator. Read `agents/orchestrator.md` and `prompts/execute_pipeline.md`.

## Environment checks

1. Confirm the working directory contains `PLAN.md` and `.cursor/commands/generate-bardolino-guide.md`.
2. Ensure `shared/` and `output/` exist.
3. Do not delete existing `output/bardolino-trip-guide.html` until a new HTML is successfully written (keep the previous file as fallback).

## Context to inject into every subagent

```
Family holiday guide generation.
Base: Bardolino, Lake Garda, Italy.
Stay: 6 days. Car every day. Apartment every night.
Baby under 6 months. Stroller. Easy walks only (≤1 hour).
Return before 18:00. Drive cap ~2 hours one way.
NOT a road trip. Every trip is Bardolino → day trip → Bardolino.
Priorities: 1 beaches 2 food 3 easy walks 4 scenery 5 stress-free.
Scoring: parking 20% baby 20% beauty 15% food 15% walking 10% safety 10% effort 10%.
Mandatory trips: Venice (mode to be decided) + Lake Garda boat/ferry.
Exactly four trips in the final HTML.
Deliverable: output/bardolino-trip-guide.html (single offline file).
```

## Then

Execute the pipeline. Do not wait for a second human message.
