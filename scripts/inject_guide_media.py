#!/usr/bin/env python3
"""Generate guide media + trip data into the offline HTML.

Source of truth for trip content: shared/itinerary.json
This script emits `const TRIPS` (plus PHOTOS / LINKS helpers) into
output/bardolino-trip-guide.html. Opening the HTML needs no build step;
running this script is build-time codegen only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "bardolino-trip-guide.html"
CATALOG = ROOT / "output" / "images" / "catalog.json"
ITINERARY = ROOT / "shared" / "itinerary.json"

TRIPS_BEGIN = "    /* BEGIN_GENERATED_TRIPS */\n"
TRIPS_END = "\n    /* END_GENERATED_TRIPS */"

# Place + parking: Google Maps search URLs and official operator/tourism pages.
# Parking "official" is the operator or comune mobility page — never a random blog.
LINKS = {
    "sigurta-borghetto": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Parco+Giardino+Sigurt%C3%A0+Via+Cavour+1+Valeggio+sul+Mincio",
        "placeOfficial": "https://www.sigurta.it/",
        "placeOfficialLabel": "Official site — Sigurtà",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Parco+Giardino+Sigurt%C3%A0+Via+Cavour+Valeggio",
        "parkingOfficial": "https://www.sigurta.it/",
        "parkingOfficialLabel": "How to arrive — sigurta.it",
    },
    "bardolino-wine-oil": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Museo+del+Vino+Zeni+Via+Costabella+9+Bardolino",
        "placeOfficial": "https://www.zeni.it/",
        "placeOfficialLabel": "Official site — Cantina Zeni",
        "placeOfficial2": "https://www.bardolinotop.it/",
        "placeOfficial2Label": "Bardolino tourism",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Cantina+Zeni+visitor+parking+Via+Costabella+9+Bardolino",
        "parkingOfficial": "https://www.zeni.it/",
        "parkingOfficialLabel": "Visitor parking — zeni.it",
    },
    "garda-ferry": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Imbarcadero+Bardolino+Navigazione+Laghi",
        "placeOfficial": "https://www.navigazionelaghi.it/",
        "placeOfficialLabel": "Official site — Navigazione Laghi",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Imbarcadero+Bardolino",
        "parkingOfficial": "https://www.comune.bardolino.vr.it/",
        "parkingOfficialLabel": "Comune di Bardolino",
    },
    "cavaion-wine": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Cavaion+Veronese+cantine",
        "placeOfficial": "https://www.comune.cavaionveronese.vr.it/it",
        "placeOfficialLabel": "Comune di Cavaion Veronese",
        "placeOfficial2": "https://consorziobardolino.it/enoturismo/",
        "placeOfficial2Label": "Consorzio Bardolino — wineries",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Cavaion+Veronese+parcheggio",
        "parkingOfficial": "https://www.comune.cavaionveronese.vr.it/it",
        "parkingOfficialLabel": "Comune di Cavaion Veronese",
    },
    "cisano-base": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Cisano+Bardolino+spiaggia+lungolago",
        "placeOfficial": "https://www.bardolinotop.it/",
        "placeOfficialLabel": "Official site — Bardolino tourism",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Cisano+Bardolino+lungolago",
        "parkingOfficial": "https://www.comune.bardolino.vr.it/",
        "parkingOfficialLabel": "Comune di Bardolino",
    },
    "castellaro-lagusello": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Castellaro+Lagusello",
        "placeOfficial": "https://borghipiubelliditalia.it/borgo/castellaro-lagusello/",
        "placeOfficialLabel": "Official page — I Borghi più belli",
        "placeOfficial2": "https://www.comune.monzambano.mn.it/",
        "placeOfficial2Label": "Comune di Monzambano",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Castellaro+Lagusello+Via+Castello",
        "parkingOfficial": "https://www.comune.monzambano.mn.it/",
        "parkingOfficialLabel": "Comune di Monzambano",
    },
    "peschiera-lido": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Peschiera+del+Garda+centro+fortezza",
        "placeOfficial": "https://www.comune.peschieradelgarda.vr.it/",
        "placeOfficialLabel": "Comune di Peschiera del Garda",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Fortezza+Peschiera+del+Garda",
        "parkingOfficial": "https://www.comune.peschieradelgarda.vr.it/",
        "parkingOfficialLabel": "Comune parking / mobility",
    },
    "soave": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Castello+di+Soave",
        "placeOfficial": "https://www.castellodisoave.it/",
        "placeOfficialLabel": "Official site — Castello di Soave",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Castello+Soave",
        "parkingOfficial": "https://www.comune.soave.vr.it/",
        "parkingOfficialLabel": "Comune di Soave",
    },
    "garda-town": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Garda+VR+lungolago",
        "placeOfficial": "https://www.comune.garda.vr.it/",
        "placeOfficialLabel": "Comune di Garda",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Via+dei+Mulini+Garda+VR",
        "parkingOfficial": "https://www.comune.garda.vr.it/",
        "parkingOfficialLabel": "Comune di Garda",
    },
    "valpolicella-sangiorgio": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=San+Giorgio+di+Valpolicella",
        "placeOfficial": "https://www.comune.santambrogio.vr.it/",
        "placeOfficialLabel": "Comune di Sant'Ambrogio",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Piazza+della+Pieve+San+Giorgio+di+Valpolicella+parcheggio",
        "parkingOfficial": "https://www.comune.santambrogio.vr.it/",
        "parkingOfficialLabel": "Comune di Sant'Ambrogio",
    },
    "lazise": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Lazise+centro+storico",
        "placeOfficial": "https://www.comune.lazise.vr.it/",
        "placeOfficialLabel": "Comune di Lazise",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Lazise+centro+mura",
        "parkingOfficial": "https://www.comune.lazise.vr.it/",
        "parkingOfficialLabel": "Comune di Lazise",
    },
    "torri-car": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Torri+del+Benaco+castello",
        "placeOfficial": "https://www.comune.torridelbenaco.vr.it/",
        "placeOfficialLabel": "Comune di Torri del Benaco",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Torri+del+Benaco+imbarcadero",
        "parkingOfficial": "https://www.comune.torridelbenaco.vr.it/",
        "parkingOfficialLabel": "Comune di Torri del Benaco",
    },
    "mantova": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Palazzo+Ducale+Mantova",
        "placeOfficial": "https://www.comune.mantova.it/",
        "placeOfficialLabel": "Comune di Mantova",
        "placeOfficial2": "https://www.mantovaducale.beniculturali.it/en/",
        "placeOfficial2Label": "Palazzo Ducale",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Castello+Mantova+ASTER",
        "parkingOfficial": "https://www.aster.mn.it/turisti/parcheggi-in-struttura",
        "parkingOfficialLabel": "ASTER parking (Castello / Pradella)",
        "parkingNote": "Pallone is a square, not a garage. Use ASTER Parcheggio Castello (next to Palazzo Ducale) or Pradella. Stay outside the ZTL.",
    },
    "desenzano": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Desenzano+del+Garda+porto",
        "placeOfficial": "https://www.comune.desenzano.brescia.it/",
        "placeOfficialLabel": "Comune di Desenzano del Garda",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+porto+Desenzano+del+Garda",
        "parkingOfficial": "https://www.comune.desenzano.brescia.it/",
        "parkingOfficialLabel": "Comune di Desenzano",
    },
    "salo": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Sal%C3%B2+Lungolago+Zanardelli",
        "placeOfficial": "https://www.comune.salo.bs.it/",
        "placeOfficialLabel": "Comune di Salò",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Lungolago+Zanardelli+Sal%C3%B2",
        "parkingOfficial": "https://www.comune.salo.bs.it/",
        "parkingOfficialLabel": "Comune di Salò",
    },
    "garda-punta": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Baia+delle+Sirene+Punta+San+Vigilio",
        "placeOfficial": "https://www.baiadellesirene.com/",
        "placeOfficialLabel": "Official site — Baia delle Sirene",
        "placeOfficial2": "https://www.locanda-sanvigilio.it/",
        "placeOfficial2Label": "Locanda San Vigilio",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Baia+delle+Sirene+Punta+San+Vigilio",
        "parkingOfficial": "https://www.baiadellesirene.com/",
        "parkingOfficialLabel": "Bay parking — baiadellesirene.com",
    },
    "vicenza": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Piazza+dei+Signori+Vicenza",
        "placeOfficial": "https://www.vicenzae.org/",
        "placeOfficialLabel": "Official tourism — Vicenzaè",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Piazza+Castello+Vicenza",
        "parkingOfficial": "https://www.comune.vicenza.it/",
        "parkingOfficialLabel": "Comune di Vicenza",
    },
    "verona": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Arena+di+Verona",
        "placeOfficial": "https://www.visitverona.it/en",
        "placeOfficialLabel": "Official tourism — VisitVerona",
        "placeOfficial2": "https://www.arena.it/",
        "placeOfficial2Label": "Arena di Verona",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Saba+Arena+Via+Bentegodi+Verona",
        "parkingOfficial": "https://www.sabait.it/it/parcheggio-verona/parcheggio-saba-arena",
        "parkingOfficialLabel": "Saba Arena garage",
    },
    "padova": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Prato+della+Valle+Padova",
        "placeOfficial": "https://www.turismopadova.it/",
        "placeOfficialLabel": "Official tourism — Padova",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Piazza+Rabin+Prato+della+Valle+Padova",
        "parkingOfficial": "https://www.comune.padova.it/elenco-parcheggi-citta",
        "parkingOfficialLabel": "Padova parking list",
    },
    "brescia": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Piazza+della+Loggia+Brescia",
        "placeOfficial": "https://www.visitbrescia.it/",
        "placeOfficialLabel": "Official tourism — VisitBrescia",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Piazza+della+Vittoria+Brescia",
        "parkingOfficial": "https://www.bresciamobilita.it/",
        "parkingOfficialLabel": "Brescia Mobilità parking",
    },
    "sirmione": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Castello+Scaligero+Sirmione",
        "placeOfficial": "https://visitsirmione.com/en/",
        "placeOfficialLabel": "Official tourism — Visit Sirmione",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Monte+Baldo+Sirmione",
        "parkingOfficial": "https://www.sirmiopark.com/",
        "parkingOfficialLabel": "SirmioPark (live spaces)",
        "parkingOfficial2": "https://www.sirmioneservizi.it/grifo-parking",
        "parkingOfficial2Label": "Sirmione Servizi parking",
    },
    "venice-train": {
        "placeMaps": "https://www.google.com/maps/search/?api=1&query=Venezia+Santa+Lucia",
        "placeOfficial": "https://www.veneziaunica.it/",
        "placeOfficialLabel": "Official site — Venezia Unica",
        "placeOfficial2": "https://www.trenitalia.com/",
        "placeOfficial2Label": "Trenitalia tickets",
        "parkingMaps": "https://www.google.com/maps/search/?api=1&query=Parcheggio+Stazione+Peschiera+del+Garda+Piazzale+Stazione",
        "parkingOfficial": "https://www.fspark.it/it/parcheggi/nord-est-italia/peschiera-del-garda.html",
        "parkingOfficialLabel": "FS Park — Peschiera station",
    },
}

CSS = """
    .card-photo {
      width: calc(100% + 48px); max-width: none;
      margin: -24px -24px 4px; height: 180px; object-fit: cover; display: block;
      border-radius: var(--radius) var(--radius) 0 0; background: var(--sand);
    }
    .gallery { display: flex; flex-direction: column; gap: 8px; }
    .gallery-hero { margin: 0; }
    .gallery-hero img {
      width: 100%; height: 280px; object-fit: cover; display: block;
      border-radius: var(--radius); background: var(--sand);
    }
    .gallery-thumbs {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
    }
    .gallery-thumbs img {
      width: 100%; height: 96px; object-fit: cover; display: block;
      border-radius: 10px; background: var(--sand);
    }
    .gallery figcaption, .photo-credit {
      margin: 6px 0 0; font-size: var(--fs-k); color: var(--ink-soft);
    }
    .link-block { margin-top: 12px; }
    .link-block h4 {
      margin: 0 0 8px; font-size: var(--fs-k); letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--ink-soft); font-weight: 650;
    }
    .link-row { display: flex; flex-wrap: wrap; gap: 8px; }
    .link-row .btn { font-size: var(--fs-s); }
    .visual { grid-template-columns: 1fr; }
"""

JS_HELPERS = r"""
      const PHOTOS = __PHOTOS__;
      const LINKS = __LINKS__;

      function photosOf(trip) {
        return PHOTOS[trip.id] || [];
      }
      function linkOf(trip) {
        return LINKS[trip.id] || {};
      }
      function extBtn(href, label, primary) {
        if (!href) return "";
        var cls = primary ? "btn" : "btn ghost";
        return '<a class="' + cls + '" href="' + esc(href) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + "</a>";
      }
      function placeLinksHtml(trip) {
        var L = linkOf(trip);
        var maps = L.placeMaps || trip.mapsUrl;
        return '<div class="link-block"><h4>Place links</h4><div class="link-row">' +
          extBtn(maps, "Google Maps — place", true) +
          extBtn(L.placeOfficial, L.placeOfficialLabel || "Official site", false) +
          extBtn(L.placeOfficial2, L.placeOfficial2Label || "Official site", false) +
          "</div></div>";
      }
      function parkingLinksHtml(trip) {
        var L = linkOf(trip);
        var maps = L.parkingMaps || trip.mapsUrl;
        var note = L.parkingNote ? "<p>" + esc(L.parkingNote) + "</p>" : "";
        return note + '<div class="link-block"><h4>Parking links</h4><div class="link-row">' +
          extBtn(maps, "Google Maps — parking", true) +
          extBtn(L.parkingOfficial, L.parkingOfficialLabel || "Parking operator", false) +
          extBtn(L.parkingOfficial2, L.parkingOfficial2Label || "Parking info", false) +
          "</div></div>";
      }
      function galleryHtml(trip) {
        var photos = photosOf(trip);
        if (!photos.length) return coverSvg(trip);
        var main = photos[0];
        var thumbs = photos.slice(1).map(function (p) {
          return '<img src="' + esc(p.src) + '" alt="' + esc(p.alt || trip.name) + '" loading="lazy">';
        }).join("");
        return '<div class="gallery"><figure class="gallery-hero">' +
          '<img src="' + esc(main.src) + '" alt="' + esc(main.alt || trip.name) + '">' +
          (main.credit ? '<figcaption>' + esc(main.credit) + "</figcaption>" : "") +
          "</figure>" +
          (thumbs ? '<div class="gallery-thumbs">' + thumbs + "</div>" : "") +
          "</div>";
      }
"""


SKIP_FILES = {
    "cisano-base-2.jpg",  # ISS crop of the north lake
    "garda-town-1.jpg",  # Malcesine, not Garda town
    "garda-town-4.jpg",  # duplicate photochrom of town-3
    "brescia-2.jpg",  # memorial plaque, not the piazza
}


def photos_payload() -> dict:
    raw = json.loads(CATALOG.read_text()) if CATALOG.exists() else {}
    out = {}
    for trip_id, items in raw.items():
        cleaned = []
        for item in items:
            src = item.get("src") or (f"images/{item['file']}" if item.get("file") else None)
            if not src:
                continue
            fname = Path(src).name
            if fname in SKIP_FILES:
                continue
            path = ROOT / "output" / src
            if not path.exists() or path.stat().st_size < 40_000:
                continue
            alt = item.get("alt") or item.get("title") or trip_id
            alt = re.sub(r"^File:", "", str(alt))
            alt = re.sub(r"\.(jpe?g|png|webp|gif|JPG)$", "", alt)
            alt = alt.replace("_", " ").strip()
            credit = item.get("credit") or "Wikimedia Commons"
            credit = re.sub(r"<[^>]+>", "", str(credit))
            credit = re.sub(r"\s+", " ", credit).strip() or "Wikimedia Commons"
            if "Wolfgang Moroder" in credit:
                credit = "Wolfgang Moroder · CC BY-SA 3.0"
            if " · " in credit:
                parts = [p.strip() for p in credit.split(" · ") if p.strip()]
                credit = " · ".join(parts[:2])
            if len(credit) > 90:
                credit = credit[:87].rstrip() + "…"
            cleaned.append({"src": src, "alt": alt, "credit": credit})
        out[trip_id] = cleaned[:4]
    return out


def _parking_word(difficulty: str | None) -> str:
    text = (difficulty or "").strip().lower()
    for word in ("severe", "hard", "moderate", "easy"):
        if text.startswith(word) or f" {word}" in text or text == word:
            return word
    first = re.split(r"[\s—\-–,]", text, maxsplit=1)[0]
    return first or "moderate"


def _join_list(value) -> str:
    if isinstance(value, list):
        return "; ".join(str(v) for v in value if v)
    return str(value or "")


def trip_to_html(trip: dict) -> dict:
    """Map one itinerary.json trip into the HTML `TRIPS` object shape."""
    transport = trip.get("transport") or {}
    experience = trip.get("experience") or {}
    family = trip.get("family") or {}
    costs = trip.get("costs") or {}
    backup = trip.get("backup") or {}
    scores = dict(trip.get("scores") or {})
    if "total" not in scores and trip.get("score") is not None:
        scores["total"] = trip["score"]

    km = transport.get("driving_distance_km")
    minutes = transport.get("driving_duration_minutes")
    drive_label = f"{km} km · {minutes} min" if km is not None and minutes is not None else ""

    beaches = experience.get("beaches") or []
    tags = trip.get("tags") or []
    beach = bool(beaches) or "beach" in tags

    gems = experience.get("hidden_gems") or []
    restaurants = experience.get("restaurants") or []
    coffee_stops = experience.get("coffee_stops") or []

    timeline = []
    for step in trip.get("timeline") or []:
        timeline.append(
            {
                "t": step.get("time") or step.get("t") or "",
                "h": step.get("title") or step.get("h") or "",
                "d": step.get("detail") or step.get("d") or "",
            }
        )

    parking_diff = transport.get("parking_difficulty") or ""
    return {
        "id": trip["id"],
        "name": trip["name"],
        "short": trip.get("short") or "",
        "tags": tags,
        "scores": scores,
        "rationale": trip.get("rationale") or "",
        "leave": trip.get("best_departure") or "",
        "home": trip.get("expected_return") or "",
        "driveKm": km if km is not None else 0,
        "driveMin": minutes if minutes is not None else 0,
        "driveLabel": drive_label,
        "difficulty": trip.get("difficulty") or "moderate",
        "parkingWord": _parking_word(parking_diff),
        "beach": beach,
        "strollerWord": trip.get("stroller_word")
        or ("Yes" if str(experience.get("stroller_friendliness", "")).lower().startswith("yes") else "Mixed"),
        "cover": trip.get("cover") or "lake",
        "why": trip.get("why_selected") or "",
        "glanceDrive": trip.get("glance_drive") or (f"{minutes} min" if minutes is not None else ""),
        "mapsUrl": transport.get("maps_url") or "",
        "mapsLot": transport.get("maps_lot") or transport.get("parking_location") or "",
        "mapsAddress": transport.get("maps_address") or "",
        "timeline": timeline,
        "getting": {
            "mode": transport.get("mode_summary") or "",
            "route": transport.get("route") or "",
            "lot": transport.get("parking_location") or "",
            "cost": transport.get("parking_cost") or "",
            "difficulty": parking_diff,
            "backup": transport.get("parking_backup") or "",
            "ztl": transport.get("ztl") or "",
            "notes": transport.get("notes") or "",
        },
        "there": {
            "walk": experience.get("walking_route") or "",
            "skip": experience.get("skip") or "",
            "gem": experience.get("place_gem") or (gems[0] if gems else ""),
            "food": experience.get("place_food") or (restaurants[0] if restaurants else ""),
            "coffee": experience.get("place_coffee") or (coffee_stops[0] if coffee_stops else ""),
        },
        "babyNotes": {
            "changing": family.get("baby_changing") or "",
            "rest": family.get("places_to_rest") or "",
            "carrier": family.get("stroller_notes") or "",
            "crowds": _join_list(family.get("crowded_areas_to_avoid")),
        },
        "costs": {
            "parking": costs.get("parking") or "",
            "food": costs.get("food_estimate") or costs.get("food") or "",
            "tickets": costs.get("tickets") or "",
            "ferry": costs.get("ferry") or "€0",
        },
        "rain": backup.get("rainy_day_alternative") or "",
        "viewpoints": experience.get("viewpoints") or [],
        "restaurants": restaurants,
        "coffeeStops": coffee_stops,
        "gems": gems,
        "walkingDuration": experience.get("walking_duration") or "",
        "stroller": experience.get("stroller_friendliness") or "",
        "mandatory": bool(trip.get("mandatory")),
        "veniceModes": trip.get("venice_modes"),
        "beaches": beaches,
    }


def trips_payload() -> list[dict]:
    data = json.loads(ITINERARY.read_text(encoding="utf-8"))
    trips = data.get("trips") or []
    if len(trips) < 4:
        raise SystemExit(f"itinerary.json has too few trips ({len(trips)})")
    return [trip_to_html(t) for t in trips]


def inject_trips(html: str, trips: list[dict]) -> str:
    """Replace the TRIPS const with generated JSON between stable anchors."""
    payload = json.dumps(trips, ensure_ascii=False, separators=(",", ":"))
    block = f"{TRIPS_BEGIN}    const TRIPS = {payload};{TRIPS_END}"

    if "/* BEGIN_GENERATED_TRIPS */" in html and "/* END_GENERATED_TRIPS */" in html:
        start = html.find("/* BEGIN_GENERATED_TRIPS */")
        # rewind to line start
        line_start = html.rfind("\n", 0, start) + 1
        end = html.find("/* END_GENERATED_TRIPS */")
        if end == -1:
            raise SystemExit("END_GENERATED_TRIPS anchor missing")
        end = end + len("/* END_GENERATED_TRIPS */")
        return html[:line_start] + block + html[end:]

    # First-time wrap: replace bare `const TRIPS = ...;` before WEIGHTS
    marker = "    const TRIPS = "
    start = html.find(marker)
    if start == -1:
        raise SystemExit("const TRIPS anchor not found")
    end = html.find(";\n    const WEIGHTS", start)
    if end == -1:
        raise SystemExit("const WEIGHTS anchor after TRIPS not found")
    end += 1  # include the semicolon
    return html[:start] + block + html[end:]


def inject_css(html: str) -> str:
    needle = "    .visual {\n      display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; align-items: stretch;\n    }"
    if ".gallery-hero img" in html:
        # already injected; still refresh visual rule if old
        html = html.replace(
            "grid-template-columns: 1.2fr 0.8fr; gap: 16px; align-items: stretch;",
            "grid-template-columns: 1fr; gap: 16px; align-items: stretch;",
        )
        if ".card-photo" not in html:
            html = html.replace(needle, needle + "\n" + CSS)
        return html
    if needle not in html:
        raise SystemExit("CSS anchor not found")
    return html.replace(needle, needle + "\n" + CSS, 1)


def inject_js(html: str, photos: dict, links: dict) -> str:
    helpers = JS_HELPERS.replace("__PHOTOS__", json.dumps(photos, ensure_ascii=False)).replace(
        "__LINKS__", json.dumps(links, ensure_ascii=False)
    )
    if "const PHOTOS =" in html:
        start = html.find("      const PHOTOS =")
        end = html.find("      function coverSvg(trip)")
        if start == -1 or end == -1:
            raise SystemExit("Could not refresh PHOTOS/LINKS block")
        html = html[:start] + helpers + html[end:]
        # helpers already includes trailing functions; coverSvg follows. But we duplicated
        # the marker. helpers ends with galleryHtml; then coverSvg. Good if we sliced to coverSvg.
        # Wait: html[end:] starts with "function coverSvg" without "      "? We used find on
        # "      function coverSvg" so end includes indent. helpers.strip() loses indent of first line.
        # Re-do more carefully below if this path is used.
    else:
        anchor = "      function coverSvg(trip) {"
        if anchor not in html:
            raise SystemExit("JS coverSvg anchor not found")
        html = html.replace(anchor, helpers + "\n      function coverSvg(trip) {", 1)

    old_card = '''        rootEl.innerHTML = list.map(function (trip) {
          return '<article class="card" data-trip="' + esc(trip.id) + '">' +
            '<div class="card-top"><h3>' + esc(trip.name) + "</h3>" + scoreControl(trip) + "</div>" +'''
    new_card = '''        rootEl.innerHTML = list.map(function (trip) {
          var ph = photosOf(trip)[0];
          var img = ph ? '<img class="card-photo" src="' + esc(ph.src) + '" alt="' + esc(ph.alt || trip.name) + '">' : "";
          return '<article class="card" data-trip="' + esc(trip.id) + '">' +
            img +
            '<div class="card-top"><h3>' + esc(trip.name) + "</h3>" + scoreControl(trip) + "</div>" +'''
    if old_card not in html:
        if "var ph = photosOf(trip)[0];" not in html:
            raise SystemExit("card renderer anchor not found")
    else:
        html = html.replace(old_card, new_card, 1)

    old_place = """          '<section class="guide-ch"><h3>The place</h3><div class="visual">' + coverSvg(trip) +
            '<div class="park"><p><strong>Lot:</strong> ' + esc(trip.mapsLot) + "</p>" +
            "<p><strong>Address:</strong> " + esc(trip.mapsAddress) + "</p>" +
            '<p><a class="btn" href="' + esc(trip.mapsUrl) + '">Open Google Maps</a></p></div></div></section>' +"""
    new_place = """          '<section class="guide-ch"><h3>The place</h3><div class="visual">' + galleryHtml(trip) +
            placeLinksHtml(trip) +
            "</div></section>" +"""
    if old_place not in html:
        if "placeLinksHtml(trip)" not in html:
            raise SystemExit("place section anchor not found")
    else:
        html = html.replace(old_place, new_place, 1)

    old_park = """            (g.notes ? "<p>" + esc(g.notes) + "</p>" : "") + "</div></section>" +"""
    new_park = """            (g.notes ? "<p>" + esc(g.notes) + "</p>" : "") +
            "<p><strong>Lot:</strong> " + esc(trip.mapsLot) + "<br/><strong>Address:</strong> " + esc(trip.mapsAddress) + "</p>" +
            parkingLinksHtml(trip) + "</div></section>" +"""
    if old_park not in html:
        if "parkingLinksHtml(trip)" not in html:
            raise SystemExit("parking section anchor not found")
    else:
        html = html.replace(old_park, new_park, 1)
    return html


def main() -> None:
    photos = photos_payload()
    trips = trips_payload()
    missing = [k for k in LINKS if not photos.get(k)]
    print("photos trips", sum(1 for v in photos.values() if v), "of", len(LINKS))
    print("generated TRIPS", len(trips), "from", ITINERARY.relative_to(ROOT))
    if missing:
        print("no photos yet:", ", ".join(missing))
    html = HTML.read_text(encoding="utf-8")
    html = inject_trips(html, trips)
    html = inject_css(html)
    html = inject_js(html, photos, LINKS)
    HTML.write_text(html, encoding="utf-8")
    print("updated", HTML)


if __name__ == "__main__":
    main()
