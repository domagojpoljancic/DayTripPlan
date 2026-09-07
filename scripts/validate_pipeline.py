#!/usr/bin/env python3
"""Validate pipeline JSON and HTML hard rules. No network required."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"
OUTPUT = ROOT / "output" / "bardolino-trip-guide.html"
IMAGES = ROOT / "output" / "images"

# Keep in parity with schemas/html_requirements.md forbidden dependencies.
FORBIDDEN_HTML = [
    "cdn.",
    "unpkg",
    "fonts.googleapis",
    "fonts.gstatic",
    "cdn.jsdelivr",
    "tailwindcss.com",
    "react",
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


def extract_html_trips(html: str) -> list[dict] | None:
    """Parse generated or legacy const TRIPS from the HTML."""
    begin = html.find("/* BEGIN_GENERATED_TRIPS */")
    if begin != -1:
        chunk = html[begin:]
        m = re.search(r"const TRIPS\s*=\s*(\[.*?\]);\s*/\*\s*END_GENERATED_TRIPS\s*\*/", chunk, re.S)
        if not m:
            return None
        return json.loads(m.group(1))
    m = re.search(r"const TRIPS\s*=\s*(\[.*?\]);\s*\n\s*const WEIGHTS", html, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def referenced_image_paths(html: str, photos_block: str | None = None) -> set[str]:
    """Collect images/* paths referenced in HTML (PHOTOS payload + img src)."""
    paths: set[str] = set()
    for match in re.finditer(r"images/[A-Za-z0-9._\-]+\.(?:jpe?g|png|webp|gif)", html, re.I):
        paths.add(match.group(0))
    return paths


def check_image_integrity(html: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not IMAGES.exists():
        errors.append("missing output/images/")
        return errors, warnings

    # Duplicate content hashes across image files
    hashes: dict[str, list[str]] = {}
    for path in sorted(IMAGES.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            continue
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(path.name)
    for digest, names in hashes.items():
        if len(names) > 1:
            errors.append(f"duplicate image content (md5 {digest[:12]}…): {', '.join(names)}")

    # Missing files referenced by the guide
    for rel in sorted(referenced_image_paths(html)):
        full = ROOT / "output" / rel
        if not full.exists():
            errors.append(f"HTML references missing image: {rel}")

    return errors, warnings


def check_html_itinerary_parity(html: str, itinerary: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        html_trips = extract_html_trips(html)
    except json.JSONDecodeError as exc:
        errors.append(f"could not parse const TRIPS from HTML: {exc}")
        return errors, warnings
    if html_trips is None:
        errors.append("HTML missing parseable const TRIPS block")
        return errors, warnings

    itin_trips = itinerary.get("trips") or []
    html_ids = [t.get("id") for t in html_trips]
    itin_ids = [t.get("id") for t in itin_trips]
    if html_ids != itin_ids:
        only_html = sorted(set(html_ids) - set(itin_ids))
        only_itin = sorted(set(itin_ids) - set(html_ids))
        errors.append(
            "HTML TRIPS ids diverge from shared/itinerary.json "
            f"(html={len(html_ids)} itin={len(itin_ids)}; "
            f"only_html={only_html or '—'}; only_itin={only_itin or '—'}; "
            f"order_match={html_ids == itin_ids})"
        )

    # Mandatory trip presence warning
    mandatory = [t for t in itin_trips if t.get("mandatory")]
    if not mandatory:
        warnings.append("no mandatory trips flagged in itinerary.json")
    else:
        names = " ".join(t.get("name", "").lower() for t in mandatory)
        if "venice" not in names and "venezia" not in names:
            warnings.append("mandatory set missing Venice")
        if "ferry" not in names and "boat" not in names and "battello" not in names:
            warnings.append("mandatory set missing ferry/boat day")
        html_by_id = {t.get("id"): t for t in html_trips}
        for t in mandatory:
            ht = html_by_id.get(t.get("id"))
            if not ht:
                errors.append(f"mandatory trip {t.get('id')} missing from HTML TRIPS")
            elif not ht.get("mandatory"):
                errors.append(f"mandatory trip {t.get('id')} not flagged mandatory in HTML")

    return errors, warnings


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
        itinerary = None
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
        html = ""
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

        img_errs, img_warns = check_image_integrity(html)
        errors.extend(img_errs)
        warnings.extend(img_warns)

        if itinerary:
            parity_errs, parity_warns = check_html_itinerary_parity(html, itinerary)
            errors.extend(parity_errs)
            warnings.extend(parity_warns)

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
