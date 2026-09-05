# Review

Use when an agent output is invalid, thin, or contradictory.

## For the Orchestrator

Paste this into a retry Task:

```
Your previous output failed review.
Target file: <path>
Errors:
- <schema / missing field / contradiction>

Re-read your agent spec and the schema.
Rewrite the ENTIRE output file.
Do not apologize. Do not keep the broken version.
Family constraints still apply (Bardolino loops, 18:00, infant, stroller, parking honesty).
```

## Common failures to look for

- JSON trailing commentary
- Venice winner with no comparison table
- Ferry day that is actually a 7-hour Riva cruise
- Sirmione as a scored “easy parking” destination
- Fifth trip smuggled into the HTML
- External CSS/JS
- Return times after 18:00
- “Parking nearby” without a lot name
- Stroller-friendly Venice

## For QA-driven review

If `shared/qa_report.md` lists blocking items, send Final Polish those items verbatim. Do not summarize away the parking lot name that was missing.
