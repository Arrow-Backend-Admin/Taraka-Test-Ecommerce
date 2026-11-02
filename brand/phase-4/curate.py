"""Fetch the shortlisted placeholder sources at review size.

Curation helper. It resolves exact Commons file titles, records licence and
attribution metadata, downloads 800 px previews for visual QA and writes a
contact sheet. The final derivatives are built by ``build_placeholders.py``.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
QA_DIR = ROOT / "qa"
CURATED_DIR = QA_DIR / "curated"
MANIFEST = QA_DIR / "curated.json"
USER_AGENT = "SantvanaPlaceholderCuration/1.0 (concept project)"

PICKS: dict[str, dict[str, str | None]] = {
    "sneakers": {
        "hero-45": "File:Simple Sneakers (Unsplash).jpg",
        "lateral": "File:White sneakers on asphalt (Unsplash).jpg",
        "heel": "File:Sneakers on black cubes (Unsplash).jpg",
        "top-down": "File:Sneaker on a beach tree (Unsplash).jpg",
        "sole-macro": None,
        "on-foot": "File:Guy running in sneakers (Unsplash).jpg",
    },
    "running": {
        "hero-45": "File:Womens pink running shoes (Unsplash).jpg",
        "lateral": "File:Aarhus, Denmark (Unsplash t1sTHYjSN10).jpg",
        "heel": None,
        "top-down": "File:Aarhus, Denmark (Unsplash wmdcUQ0CJ4c).jpg",
        "sole-macro": None,
        "on-foot": "File:Sprinting in Vienna (Unsplash).jpg",
    },
    "sandals": {
        "hero-45": "File:Man in sport sandals front view.jpg",
        "lateral": "File:Man in sandals side view.jpg",
        "heel": "File:Man in sandals 2.jpg",
        "top-down": "File:Man in sandals top view.jpg",
        "sole-macro": None,
        "on-foot": "File:Man in sandals toe view.jpg",
    },
    "boots": {
        "hero-45": "File:Brown leather boots on a wood floor (Unsplash).jpg",
        "lateral": "File:Boots (Unsplash).jpg",
        "heel": "File:Boots on a rock (Unsplash).jpg",
        "top-down": "File:Hiking Boots (Unsplash).jpg",
        "sole-macro": "File:Boots on the beach (Unsplash).jpg",
        "on-foot": "File:Wearing boots on the pier (Unsplash).jpg",
    },
    "everyday": {
        "hero-45": "File:Man wearing loafers (Unsplash).jpg",
        "lateral": "File:Leather shoes over a creek (Unsplash).jpg",
        "heel": "File:Man shoes (Unsplash).jpg",
        "top-down": "File:Shoes and tie in flatlay (Unsplash).jpg",
        "sole-macro": None,
        "on-foot": "File:Boat shoes and jeans (Unsplash).jpg",
    },
}


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _strip(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def _licence_url(name: str, version: str) -> str:
    key = name.strip().lower().replace(" ", "-")
    if key == "cc0":
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    if key.startswith("cc-by"):
        return f"https://creativecommons.org/licenses/by/{version or '4.0'}/"
    return ""


def resolve(title: str) -> dict | None:
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": "900",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    payload: dict = {}
    for attempt in range(4):
        try:
            payload = json.loads(_get(url))
            if payload.get("query"):
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(2 * (attempt + 1))
    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page:
            return None
        info = (page.get("imageinfo") or [{}])[0]
        metadata = info.get("extmetadata", {})
        licence = _strip(metadata.get("LicenseShortName", {}).get("value"))
        version = _strip(metadata.get("LicenseVersion", {}).get("value"))
        if not (licence.lower() == "cc0" or licence.lower().startswith("cc by")):
            return None
        return {
            "title": page.get("title", title),
            "licence_name": licence,
            "licence_version": version or ("1.0" if licence.lower() == "cc0" else ""),
            "licence_url": _strip(metadata.get("LicenseUrl", {}).get("value"))
            or _licence_url(licence, version),
            "photographer": _strip(metadata.get("Artist", {}).get("value")),
            "credit": _strip(metadata.get("Credit", {}).get("value")),
            "description": _strip(metadata.get("ImageDescription", {}).get("value")),
            "source_url": "https://commons.wikimedia.org/wiki/"
            + urllib.parse.quote(page.get("title", title).replace(" ", "_")),
            "download_url": info.get("url"),
            "preview_url": info.get("thumburl"),
            "width": info.get("width"),
            "height": info.get("height"),
        }
    return None


def contact_sheet(records: list[dict]) -> Path:
    columns = 6
    tile_w, tile_h, label_h = 200, 200, 38
    rows = (len(records) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_w, rows * (tile_h + label_h)), "#f4f2ed")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    for position, record in enumerate(records):
        row, column = divmod(position, columns)
        x, y = column * tile_w, row * (tile_h + label_h)
        path = CURATED_DIR / record["category"] / f"{record['role']}.jpg"
        try:
            with Image.open(path) as image:
                image.thumbnail((tile_w - 8, tile_h - 8))
                sheet.paste(image.convert("RGB"), (x + 4, y + 4))
        except OSError:
            draw.rectangle([x + 4, y + 4, x + tile_w - 4, y + tile_h - 4], fill="#cccccc")
        draw.text(
            (x + 4, y + tile_h + 2),
            f"{record['category']} / {record['role']}",
            fill="#222222",
            font=font,
        )
        draw.text(
            (x + 4, y + tile_h + 18),
            record["licence_name"][:30],
            fill="#555555",
            font=font,
        )
    path = QA_DIR / "sheets" / "curated.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=90)
    return path


def main() -> None:
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    missing: list[str] = []
    for category, roles in PICKS.items():
        for role, title in roles.items():
            if not title:
                continue
            resolved = resolve(title)
            if resolved is None:
                missing.append(f"{category}/{role}: {title}")
                continue
            destination = CURATED_DIR / category / f"{role}.jpg"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                try:
                    destination.write_bytes(_get(resolved["preview_url"]))
                except (urllib.error.URLError, TimeoutError) as exc:
                    missing.append(f"{category}/{role}: download failed ({exc})")
                    continue
            record = {"category": category, "role": role, **resolved}
            records.append(record)
            time.sleep(1.0)

    MANIFEST.write_text(
        json.dumps({"sources": records, "missing": missing}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"resolved {len(records)} sources; {len(missing)} missing")
    for item in missing:
        print("  missing:", item)
    if records:
        print("contact sheet:", contact_sheet(records))


if __name__ == "__main__":
    main()
