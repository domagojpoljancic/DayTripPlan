#!/usr/bin/env python3
"""Download real Wikimedia/Wikipedia photos for the Bardolino guide.

Skips coats of arms, maps, logos, and tiny files. Wikipedia's default
pageimage is often a civic emblem — we walk page images and pick large photos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "images"
CATALOG = OUT / "catalog.json"
UA = "BardolinoFamilyGuide/2.0 (travel planner; local offline copy)"
MAX_CREDIT_LEN = 90
MIN_BYTES = 40_000

# Keep in sync with scripts/inject_guide_media.py — never write these filenames.
SKIP_FILES = {
    "cisano-base-2.jpg",
    "garda-town-1.jpg",
    "garda-town-4.jpg",
    "brescia-2.jpg",
}

SKIP_NAME = re.compile(
    r"coat|flag|logo|icon|map|location|commons-logo|wikipedia|wikimedia|"
    r"edit[-_ ]icon|padlock|speaker|symbol|seal|stemma|wappen|crest|"
    r"banner|wordmark|signature|qr.?code|pictogram|silhouette|"
    r"disambig|stub|portal|ambox|copyright|cc-by|red_pog|dot|"
    r"increase|decrease|crystal|gnome|nuvola|kit_|football|coa\b|"
    r"blason|herald|escudo|armoir",
    re.I,
)

TRIPS = {
    "sigurta-borghetto": [
        ("commons-search", "Parco Giardino Sigurtà"),
        ("wiki", "en", "Sigurtà Garden Park"),
        ("commons-search", "Borghetto Valeggio sul Mincio"),
        ("wiki", "it", "Borghetto (Valeggio sul Mincio)"),
    ],
    "bardolino-wine-oil": [
        ("commons-search", "Bardolino lakefront"),
        ("wiki", "en", "Bardolino"),
        ("commons-search", "Museo dell'Olio Zeni Bardolino"),
        ("wiki", "it", "Bardolino"),
    ],
    "garda-ferry": [
        ("commons-search", "Ferry Lake Garda Peschiera"),
        ("wiki", "en", "Navigazione Laghi"),
        ("commons-search", "Traghetto Lago di Garda"),
        ("wiki", "it", "Lago di Garda"),
    ],
    "cavaion-wine": [
        ("commons-search", "Cavaion Veronese vineyards"),
        ("commons-search", "Cavaion Veronese panorama"),
        ("wiki", "it", "Cavaion Veronese"),
        ("commons-search", "wine Bardolino"),
        ("wiki", "it", "Bardolino (vino)"),
        ("commons-search", "Bardolino DOC vineyards"),
    ],
    "cisano-base": [
        ("commons-search", "Cisano di Bardolino porto"),
        ("commons-search", "Cisano Bardolino beach"),
        ("wiki", "it", "Cisano (Bardolino)"),
        ("commons-search", "Lungolago Cisano Bardolino"),
    ],
    "castellaro-lagusello": [
        ("commons-search", "Castellaro Lagusello"),
        ("wiki", "it", "Castellaro Lagusello"),
        ("commons-search", "Monzambano lago"),
    ],
    "peschiera-lido": [
        ("commons-search", "Peschiera del Garda fortress"),
        ("wiki", "en", "Peschiera del Garda"),
        ("commons-search", "Peschiera del Garda lungolago"),
        ("wiki", "it", "Peschiera del Garda"),
    ],
    "soave": [
        ("commons-search", "Castello di Soave"),
        ("wiki", "en", "Soave, Veneto"),
        ("commons-search", "Soave castle walls"),
        ("wiki", "it", "Soave (Italia)"),
    ],
    "garda-town": [
        ("commons-search", "Garda Italy waterfront"),
        ("wiki", "en", "Garda, Veneto"),
        ("commons-search", "Garda Verona porto"),
        ("wiki", "it", "Garda (Italia)"),
    ],
    "valpolicella-sangiorgio": [
        ("commons-search", "Sant'Ambrogio di Valpolicella"),
        ("wiki", "en", "Valpolicella"),
        ("commons-search", "San Giorgio Valpolicella"),
        ("wiki", "it", "Sant'Ambrogio di Valpolicella"),
    ],
    "lazise": [
        ("commons-search", "Lazise castle harbour"),
        ("wiki", "en", "Lazise"),
        ("commons-search", "Lazise porto"),
        ("wiki", "it", "Lazise"),
    ],
    "torri-car": [
        ("commons-search", "Torri del Benaco castle"),
        ("wiki", "en", "Torri del Benaco"),
        ("commons-search", "Torri del Benaco porto"),
        ("wiki", "it", "Torri del Benaco"),
    ],
    "mantova": [
        ("commons-search", "Palazzo Ducale Mantova"),
        ("wiki", "en", "Mantua"),
        ("commons-search", "Mantova centro storico"),
        ("wiki", "it", "Mantova"),
    ],
    "desenzano": [
        ("commons-search", "Desenzano del Garda harbour"),
        ("wiki", "en", "Desenzano del Garda"),
        ("commons-search", "Desenzano porto"),
        ("wiki", "it", "Desenzano del Garda"),
    ],
    "salo": [
        ("commons-search", "Salò Lungolago"),
        ("wiki", "en", "Salò"),
        ("commons-search", "Salò lago di Garda"),
        ("wiki", "it", "Salò"),
    ],
    "garda-punta": [
        ("commons-search", "Punta San Vigilio Garda"),
        ("wiki", "en", "Punta San Vigilio"),
        ("commons-search", "Baia delle Sirene Garda"),
        ("commons-search", "San Vigilio Lake Garda"),
    ],
    "vicenza": [
        ("commons-search", "Basilica Palladiana Vicenza"),
        ("wiki", "en", "Vicenza"),
        ("commons-search", "Piazza dei Signori Vicenza"),
        ("wiki", "it", "Vicenza"),
    ],
    "verona": [
        ("commons-search", "Arena di Verona"),
        ("wiki", "en", "Verona"),
        ("commons-search", "Piazza delle Erbe Verona"),
        ("wiki", "it", "Verona"),
        ("commons-search", "Ponte Pietra Verona"),
    ],
    "padova": [
        ("commons-search", "Prato della Valle Padova"),
        ("wiki", "en", "Padua"),
        ("commons-search", "Piazza dei Signori Padova"),
        ("wiki", "it", "Padova"),
    ],
    "brescia": [
        ("commons-search", "Piazza della Loggia Brescia"),
        ("wiki", "en", "Brescia"),
        ("commons-search", "Capitolium Brescia"),
        ("wiki", "it", "Brescia"),
    ],
    "sirmione": [
        ("commons-search", "Castello Scaligero Sirmione"),
        ("wiki", "en", "Sirmione"),
        ("commons-search", "Sirmione peninsula"),
        ("wiki", "it", "Sirmione"),
    ],
    "venice-train": [
        ("commons-search", "Grand Canal Venice"),
        ("wiki", "en", "Venice"),
        ("commons-search", "Piazza San Marco Venice"),
        ("wiki", "it", "Venezia"),
        ("commons-search", "Santa Lucia railway station Venice"),
    ],
}


def urlopen(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    last_err = None
    for attempt in range(5):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2.5 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last_err = e
            time.sleep(1.2 * (attempt + 1))
    raise last_err


def api(url: str, params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    with urlopen(f"{url}?{q}") as r:
        return json.loads(r.read().decode("utf-8"))


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def credit_from(meta: dict) -> str:
    artist = strip_html((meta.get("Artist") or {}).get("value") or "")
    license_ = strip_html((meta.get("LicenseShortName") or {}).get("value") or "")
    credit = strip_html((meta.get("Credit") or {}).get("value") or "")
    bits = [p for p in (artist or credit, license_) if p]
    out = " · ".join(bits)[:240] if bits else "Wikimedia Commons"
    if "Wolfgang Moroder" in out:
        out = "Wolfgang Moroder · CC BY-SA 3.0"
    if " · " in out:
        parts = [p.strip() for p in out.split(" · ") if p.strip()]
        out = " · ".join(parts[:2])
    if len(out) > MAX_CREDIT_LEN:
        out = out[: MAX_CREDIT_LEN - 1].rstrip() + "…"
    return out


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def md5_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return md5_bytes(path.read_bytes())
    except OSError:
        return None


def build_hash_registry(exclude: set[str] | None = None) -> dict[str, str]:
    """Map content md5 -> filename for every image already on disk."""
    exclude = exclude or set()
    registry: dict[str, str] = {}
    for path in sorted(OUT.glob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        if path.name in exclude:
            continue
        digest = md5_file(path)
        if digest and digest not in registry:
            registry[digest] = path.name
    return registry


def is_usable_file(path: Path, registry: dict[str, str]) -> bool:
    if not path.is_file() or path.stat().st_size < MIN_BYTES:
        return False
    digest = md5_file(path)
    if not digest:
        return False
    owner = registry.get(digest)
    return owner is None or owner == path.name


def is_photo(info: dict, title: str) -> bool:
    mime = (info.get("mime") or "").lower()
    if not mime.startswith("image/"):
        return False
    if mime in ("image/svg+xml", "image/gif", "image/x-icon"):
        return False
    # Match the file title only — Wikimedia URLs always contain "wikimedia"/"wikipedia".
    if SKIP_NAME.search(title or ""):
        return False
    w = int(info.get("width") or 0)
    h = int(info.get("thumbwidth") or info.get("width") or 0)
    # Require a real photograph, not a 120px emblem
    if w < 700 and h < 700:
        return False
    if w > 0 and h > 0:
        ratio = max(w, h) / max(1, min(w, h))
        if ratio > 4.5:  # banners / strips
            return False
    return True


def pick_url(info: dict) -> str | None:
    thumb = info.get("thumburl")
    if thumb and int(info.get("thumbwidth") or 0) >= 900:
        return thumb
    return info.get("url")


def wiki_page_photos(lang: str, title: str) -> list[dict]:
    data = api(
        f"https://{lang}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "format": "json",
            "generator": "images",
            "titles": title,
            "gimlimit": "40",
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": "1400",
        },
    )
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for page in pages.values():
        title_f = page.get("title") or ""
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        if not is_photo(info, title_f):
            continue
        url = pick_url(info)
        if not url:
            continue
        out.append(
            {
                "url": url,
                "orig": info.get("url"),
                "width": info.get("width"),
                "credit": credit_from(info.get("extmetadata") or {}),
                "title": title_f,
                "source": f"wikipedia:{lang}:{title}",
            }
        )
    out.sort(key=lambda x: int(x.get("width") or 0), reverse=True)
    return out


def commons_search(query: str) -> list[dict]:
    data = api(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": "12",
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": "1400",
        },
    )
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for page in pages.values():
        title_f = page.get("title") or ""
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        if not is_photo(info, title_f):
            continue
        url = pick_url(info)
        if not url:
            continue
        out.append(
            {
                "url": url,
                "orig": info.get("url"),
                "width": info.get("width"),
                "credit": credit_from(info.get("extmetadata") or {}),
                "title": title_f,
                "source": f"commons:{query}",
            }
        )
    out.sort(key=lambda x: int(x.get("width") or 0), reverse=True)
    return out


def download(url: str, dest: Path, registry: dict[str, str]) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url, timeout=90) as r:
            data = r.read()
        if len(data) < MIN_BYTES:
            return False
        digest = md5_bytes(data)
        owner = registry.get(digest)
        if owner and owner != dest.name:
            print("  skip duplicate hash", dest.name, "matches", owner)
            return False
        dest.write_bytes(data)
        registry[digest] = dest.name
        return True
    except Exception as e:
        print("  fail", dest.name, e)
        return False


def collect_for_trip(
    queries: list[tuple],
    seen_urls: set[str],
    seen_titles: set[str],
    max_items: int = 12,
) -> list[dict]:
    found: list[dict] = []
    for kind, *rest in queries:
        if len(found) >= max_items:
            break
        try:
            if kind == "wiki":
                lang, title = rest
                batch = wiki_page_photos(lang, title)
            else:
                batch = commons_search(rest[0])
        except Exception as e:
            print("  query fail", kind, rest, e)
            time.sleep(1.5)
            continue
        time.sleep(0.85)
        for item in batch:
            key = (item.get("orig") or item["url"]).split("?")[0]
            tkey = re.sub(r"\W+", "", (item.get("title") or "")).lower()
            if key in seen_urls or tkey in seen_titles:
                continue
            seen_urls.add(key)
            seen_titles.add(tkey)
            found.append(item)
            if len(found) >= max_items:
                break
    return found


def trip_slots(trip_id: str, max_photos: int = 4) -> list[int]:
    slots = []
    for slot in range(1, max_photos + 1):
        for ext in (".jpg", ".png", ".webp"):
            if f"{trip_id}-{slot}{ext}" in SKIP_FILES:
                break
        else:
            slots.append(slot)
    return slots


def catalog_seen(exclude_trip: str | None = None) -> tuple[set[str], set[str]]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    if not CATALOG.exists():
        return seen_urls, seen_titles
    raw = json.loads(CATALOG.read_text())
    for trip_id, items in raw.items():
        if trip_id == exclude_trip:
            continue
        for item in items:
            orig = (item.get("orig") or "").split("?")[0]
            if orig:
                seen_urls.add(orig)
            tkey = re.sub(r"\W+", "", (item.get("title") or "")).lower()
            if tkey:
                seen_titles.add(tkey)
    return seen_urls, seen_titles


def entry_from(dest: Path, item: dict) -> dict:
    return {
        "file": dest.name,
        "src": f"images/{dest.name}",
        "credit": item["credit"],
        "title": item.get("title"),
        "width": item.get("width"),
        "source": item.get("source"),
        "orig": item.get("orig"),
    }


def fetch_trip(
    trip_id: str,
    queries: list[tuple],
    registry: dict[str, str],
    seen_urls: set[str],
    seen_titles: set[str],
    force: bool = False,
    max_photos: int = 4,
) -> list[dict]:
    existing: dict[int, dict] = {}
    if CATALOG.exists():
        for item in json.loads(CATALOG.read_text()).get(trip_id, []):
            m = re.match(rf"^{re.escape(trip_id)}-(\d+)\.", item.get("file", ""))
            if m:
                existing[int(m.group(1))] = item

    slots_needing: list[int] = []
    kept: dict[int, dict] = {}
    for slot in trip_slots(trip_id, max_photos):
        dest = None
        for ext in (".jpg", ".png", ".webp"):
            candidate = OUT / f"{trip_id}-{slot}{ext}"
            if f"{trip_id}-{slot}{ext}" in SKIP_FILES:
                continue
            if candidate.is_file():
                dest = candidate
                break
        if dest and not force and is_usable_file(dest, registry):
            digest = md5_file(dest)
            if digest:
                registry[digest] = dest.name
            kept[slot] = existing.get(slot) or entry_from(
                dest,
                {
                    "credit": existing.get(slot, {}).get("credit", "Wikimedia Commons"),
                    "title": existing.get(slot, {}).get("title"),
                    "width": existing.get(slot, {}).get("width"),
                    "source": existing.get(slot, {}).get("source"),
                    "orig": existing.get(slot, {}).get("orig"),
                },
            )
            continue
        if dest and dest.is_file():
            digest = md5_file(dest)
            if digest and registry.get(digest) == dest.name:
                del registry[digest]
            dest.unlink(missing_ok=True)
        slots_needing.append(slot)

    if not slots_needing and len(kept) >= len(trip_slots(trip_id, max_photos)):
        return [kept[i] for i in sorted(kept) if f"{trip_id}-{i}.jpg" not in SKIP_FILES and f"{trip_id}-{i}.png" not in SKIP_FILES][:max_photos]

    trip_seen_urls, trip_seen_titles = catalog_seen(exclude_trip=trip_id)
    merged_urls = seen_urls | trip_seen_urls
    merged_titles = seen_titles | trip_seen_titles
    items = collect_for_trip(queries, merged_urls, merged_titles, max_items=20)
    item_idx = 0
    for slot in slots_needing:
        dest_base = OUT / f"{trip_id}-{slot}"
        saved = False
        while item_idx < len(items):
            item = items[item_idx]
            item_idx += 1
            ext = ".jpg"
            url_l = item["url"].lower()
            if ".png" in url_l:
                ext = ".png"
            elif ".webp" in url_l:
                ext = ".webp"
            dest = dest_base.with_suffix(ext)
            if dest.exists() and not force and is_usable_file(dest, registry):
                kept[slot] = entry_from(dest, item)
                saved = True
                break
            if download(item["url"], dest, registry):
                kept[slot] = entry_from(dest, item)
                print("  +", dest.name, item.get("width"), item.get("title"))
                time.sleep(0.25)
                saved = True
                break
        if not saved:
            print("  ! could not fill slot", slot, "for", trip_id)

    saved_list = [kept[i] for i in sorted(kept)][:max_photos]
    print("  count", len(saved_list))
    return saved_list


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Wikimedia photos for trip guide")
    parser.add_argument(
        "--trips",
        nargs="*",
        help="Trip ids to refresh (default: all)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even when an existing file looks valid",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    trip_ids = args.trips or list(TRIPS.keys())
    unknown = [t for t in trip_ids if t not in TRIPS]
    if unknown:
        raise SystemExit(f"Unknown trip ids: {', '.join(unknown)}")

    catalog: dict[str, list[dict]] = {}
    if CATALOG.exists():
        catalog = json.loads(CATALOG.read_text())

    registry = build_hash_registry()
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for trip_id in trip_ids:
        print("==", trip_id)
        saved = fetch_trip(
            trip_id,
            TRIPS[trip_id],
            registry,
            seen_urls,
            seen_titles,
            force=args.force,
        )
        catalog[trip_id] = saved
        for item in saved:
            orig = (item.get("orig") or "").split("?")[0]
            if orig:
                seen_urls.add(orig)
            tkey = re.sub(r"\W+", "", (item.get("title") or "")).lower()
            if tkey:
                seen_titles.add(tkey)

    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    print("wrote", CATALOG)


if __name__ == "__main__":
    main()
