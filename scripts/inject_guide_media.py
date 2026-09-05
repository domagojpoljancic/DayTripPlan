#!/usr/bin/env python3
"""Inject local Wikimedia photos plus Google Maps / official links into the HTML guide."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "bardolino-trip-guide.html"
CATALOG = ROOT / "output" / "images" / "catalog.json"

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
    missing = [k for k in LINKS if not photos.get(k)]
    print("photos trips", sum(1 for v in photos.values() if v), "of", len(LINKS))
    if missing:
        print("no photos yet:", ", ".join(missing))
    html = HTML.read_text()
    html = inject_css(html)
    html = inject_js(html, photos, LINKS)
    HTML.write_text(html)
    print("updated", HTML)


if __name__ == "__main__":
    main()
