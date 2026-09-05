#!/usr/bin/env python3
"""Validate pipeline JSON and HTML hard rules. No network required."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"
OUTPUT = ROOT / "output" / "bardolino-trip-guide.html"

FORBIDDEN_HTML = [
    "cdn.",
    "unpkg",
    "fonts.googleapis",
    "cdn.jsdelivr",
    "tailwindcss.com",
]


def load_json(path: Path) -> tuple[dict | None, str | None]:
    if not path.exists():
        return None, f"missing {path.relative_to(ROOT)}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path.relative_to(ROOT)}: {exc}"


def check_destination(d: dict, idx: int) -> list[str]:
    errors: list[str] = []
    prefix = f"destinations[{idx}] ({d.get('id', '?')})"
    for key in (
        "id",
        "name",
        "category",
        "drive_km_one_way",
        "drive_minutes_one_way_typical",
        "parking",
        "baby",
        "stroller",
        "walking",
        "food",
        "safety",
        "maps_url",
        "confidence",
    ):
        if key not in d:
            errors.append(f"{prefix} missing {key}")
    parking = d.get("parking") or {}
    if parking and not parking.get("lots"):
        errors.append(f"{prefix} parking.lots empty")
    minutes = d.get("drive_minutes_one_way_typical")
    if isinstance(minutes, int) and minutes > 130:
        errors.append(f"{prefix} drive cap exceeded ({minutes} min)")
    return errors


def check_trip(t: dict, idx: int) -> list[str]:
    errors: list[str] = []
    prefix = f"trips[{idx}] ({t.get('id', '?')})"
    required = [
        "id",
        "name",
        "score",
        "why_selected",
        "difficulty",
        "best_departure",
        "expected_return",
        "transport",
        "experience",
        "family",
        "costs",
        "backup",
    ]
    for key in required:
        if key not in t:
            errors.append(f"{prefix} missing {key}")
    ret = t.get("expected_return", "")
    if ret and ret > "18:00":
        errors.append(f"{prefix} return {ret} is after 18:00")
    transport = t.get("transport") or {}
    for key in (
        "driving_distance_km",
        "driving_duration_minutes",
        "route",
        "parking_location",
        "parking_cost",
        "parking_difficulty",
        "maps_url",
    ):
        if key not in transport:
            errors.append(f"{prefix} transport missing {key}")
    costs = t.get("costs") or {}
    for key in ("parking", "food_estimate", "tickets", "ferry"):
        if key not in costs:
            errors.append(f"{prefix} costs missing {key}")
    backup = t.get("backup") or {}
    if "rainy_day_alternative" not in backup:
        errors.append(f"{prefix} missing rainy_day_alternative")
    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    research, err = load_json(SHARED / "research_data.json")
    if err:
        errors.append(err)
    else:
        dests = research.get("destinations") if research else None
        if not dests:
            errors.append("research_data.json has no destinations")
        else:
            for i, d in enumerate(dests):
                errors.extend(check_destination(d, i))

    for name in (
        "local_recommendations.json",
        "venice_plan.json",
        "scored_destinations.json",
    ):
        data, err = load_json(SHARED / name)
        if err:
            errors.append(err)
        elif name == "venice_plan.json" and data:
            if not (data.get("decision") or {}).get("winner_mode_id"):
                errors.append("venice_plan.json missing decision.winner_mode_id")
            modes = data.get("modes") or []
            if len(modes) < 4:
                errors.append("venice_plan.json must compare at least 4 modes")
        elif name == "scored_destinations.json" and data:
            scored = data.get("destinations") or []
            if len(scored) < 8:
                warnings.append("few scored destinations; expected a wide pool")

    itinerary, err = load_json(SHARED / "itinerary.json")
    if err:
        errors.append(err)
    else:
        trips = itinerary.get("trips") if itinerary else None
        if not trips or len(trips) < 4:
            errors.append(f"itinerary must contain at least 4 trips (got {len(trips or [])})")
        else:
            for i, t in enumerate(trips):
                errors.extend(check_trip(t, i))
            names = " ".join(t.get("name", "").lower() for t in trips)
            if "venice" not in names and "venezia" not in names:
                errors.append("itinerary missing Venice")
            if "ferry" not in names and "boat" not in names and "battello" not in names:
                errors.append("itinerary missing a boat/ferry trip")
        if itinerary and itinerary.get("base") != "Bardolino":
            errors.append("itinerary.base must be Bardolino")

    if not OUTPUT.exists():
        errors.append("missing output/bardolino-trip-guide.html")
    else:
        html = OUTPUT.read_text(encoding="utf-8", errors="replace")
        low = html.lower()
        if "<style" not in low:
            errors.append("HTML missing embedded CSS")
        if "<script" not in low:
            errors.append("HTML missing embedded JavaScript")
        for needle in FORBIDDEN_HTML:
            if needle in low:
                errors.append(f"HTML contains forbidden dependency: {needle}")
        for section in (
            "emergency",
            "checklist",
            "dark",
            "print",
            "favorite",
            "parking",
        ):
            if section not in low:
                warnings.append(f"HTML may be missing '{section}' copy")

    print("Italy Trip Planner — pipeline validation")
    print("========================================")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        print(f"\nFAIL ({len(errors)} error(s))")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
