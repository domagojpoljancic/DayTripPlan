# Cursor rules — Italy Trip Planner

These rules bind **every** agent. They override convenience, fame, and “typical Italy itinerary” instincts.

## Product

1. The only user-facing deliverable is `output/bardolino-trip-guide.html`.
2. Markdown, JSON, and UX specs are internal. They are not the holiday guide.
3. The HTML must work **offline**, on phone and laptop, with **no** external CSS/JS/fonts/CDNs, **no** build step, **no** framework.

## Geography

4. Base is Bardolino. Every trip starts and ends in Bardolino.
5. This is **not** a road trip. No overnight stays elsewhere. No “sleep in Venice.”
6. Return target is **before 18:00**.
7. Maximum driving is approximately **2 hours one way**. Destinations beyond that are illegal in this project.
8. Do not chain cities. One day, one primary destination (a tight pair like Borghetto + Sigurtà counts as one trip).

## Family

9. There is a baby **under 6 months** and a **stroller**.
10. Walking: up to 1 hour is acceptable. No long hikes. No physically demanding sightseeing (Grotte di Catullo full walk, Monte Baldo summit hike, Verona all-day cobbles marathon, etc.).
11. Prefer secure towns. Avoid sketchy parking structures and isolated late-evening areas. This family is home before 18:00 anyway.
12. Parking information is **mandatory and realistic**. “Parking is available” is a failure. Name the lot, the walk, the cost band, the fill-time, and the backup lot.

## Selection

13. Do not recommend a place because it is famous.
14. Score with the locked weights in `PLAN.md`. Show the math.
15. Venice is mandatory, but the **mode of access** is not. Compare driving, park-outside, train, and organized transport. Optimize for baby, stroller, comfort, stress, realistic timing. Do not auto-pick “drive to Piazza San Marco” (illegal) or “everyone drives to Piazzale Roma.”
16. The boat/ferry day is mandatory. It may be a half day. It must still return before 18:00.
17. The product is a **menu of ~18–22 same-day loops** in `shared/itinerary.json`, not a locked four-trip itinerary. Venice and the Lake Garda ferry day are **mandatory** menu entries. The family picks about **5–6** outing days across a **6-day** stay; two base/nap days at the apartment are expected. Research may include many candidates; the shipped menu is the browseable set.

## Content honesty

18. If parking is hell, say so and either drop the destination or design an early-arrival protocol. Do not hide it.
19. If Venice is hostile to strollers (it is), say so and prescribe a carrier as primary.
20. Opening hours, ferry times, and train times **change**. Publish a realistic schedule and a “verify the night before” official link. Never invent a specific train number unless sourced.
21. Costs are estimates in EUR, with ranges, not fake precision.
22. No lorem ipsum. No “welcome to your app.” No chatbot tone.

## HTML

23. Follow `schemas/html_requirements.md` exactly.
24. Inspired by Apple, Airbnb, Google Travel, Lonely Planet — a premium product, not an AI answer.
25. Must include: hero, ranking, filters, expandable sections, timeline, comparison table, maps buttons, favorites, checklists, dark mode, print mode, mobile nav, packing, baby, weather, etiquette, emergency, tourist traps, rainy-day plan.

## Agent conduct

26. Write files. Do not chat about writing files.
27. Honor schemas. Invalid JSON is a failed run.
28. Never delete another agent’s `shared/` file; merge or overwrite only your assigned output path.
29. If data is uncertain, mark `"confidence": "low"` and give a verification action. Do not silently guess.
30. The user is not a coordinator. Do not ask them to choose among agents, destinations, or design systems.
