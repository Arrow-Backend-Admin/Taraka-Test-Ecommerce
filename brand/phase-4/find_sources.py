"""Search Wikimedia Commons for candidate placeholder photographs.

This is a curation helper, not a runtime dependency. It queries the Commons
API, keeps only CC0 and CC BY files, caches 320 px previews and builds contact
sheets so a human can review every candidate before it is added to
``placeholder-sources.json``.

Usage::

    python brand/phase-4/find_sources.py

The output lives in ``brand/phase-4/qa/`` and is ignored by git except for the
candidate manifest, which is useful for audit.
"""

from __future__ import annotations

import argparse
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
CANDIDATE_DIR = QA_DIR / "candidates"
SHEET_DIR = QA_DIR / "sheets"
MANIFEST = QA_DIR / "candidates.json"

USER_AGENT = "SantvanaPlaceholderCuration/1.0 (concept project)"

CATEGORIES = {
    "sneakers": [
        "sneakers",
        "canvas sneakers",
        "white sneakers",
        "high top sneakers",
        "sneaker pair",
        "sneaker side view",
    ],
    "running": [
        "running shoes",
        "jogging shoes",
        "athletic shoes",
        "running shoe pair",
        "running shoes side view",
        "running shoes sole",
    ],
    "sandals": [
        "sandals",
        "leather sandals",
        "flat sandals",
        "summer sandals",
        "sandal pair",
        "sandal sole",
    ],
    "boots": [
        "boots",
        "leather boots",
        "ankle boots",
        "hiking boots",
        "boot pair",
        "boot sole",
    ],
    "everyday": [
        "leather shoes",
        "casual shoes",
        "loafers",
        "derby shoes",
        "oxford shoes",
        "shoe side view",
    ],
}

LICENCE_OK = re.compile(r"^(CC0|CC BY(?!-SA|-NC|-ND))", re.IGNORECASE)
ALLOWED = {"cc0", "cc by 4.0", "cc by 3.0", "cc by 2.5", "cc by 2.0", "cc by 1.0"}


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def _strip(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def _licence_ok(name: str) -> bool:
    key = name.strip().lower()
    if key in ALLOWED:
        return True
    return bool(LICENCE_OK.match(name.strip()))


def search(query: str, limit: int = 20) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": "320",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        payload = json.loads(_get(url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    pages = payload.get("query", {}).get("pages", {})
    results: list[dict] = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        metadata = info.get("extmetadata", {})
        licence = _strip(metadata.get("LicenseShortName", {}).get("value"))
        if not _licence_ok(licence):
            continue
        thumb = info.get("thumburl")
        if not thumb:
            continue
        results.append(
            {
                "title": page.get("title", ""),
                "licence": licence,
                "photographer": _strip(metadata.get("Artist", {}).get("value")),
                "credit": _strip(metadata.get("Credit", {}).get("value")),
                "description": _strip(metadata.get("ImageDescription", {}).get("value")),
                "source_url": "https://commons.wikimedia.org/wiki/"
                + urllib.parse.quote(page.get("title", "").replace(" ", "_")),
                "download_url": info.get("url"),
                "thumb_url": thumb,
                "width": info.get("width"),
                "height": info.get("height"),
            }
        )
    return results


def _safe_name(index: int, title: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]
    return f"{index:03d}-{stem or 'file'}"


def _contact_sheet(category: str, items: list[dict], part: int, columns: int = 6) -> Path:
    thumb_w, thumb_h, label_h = 180, 180, 34
    rows = (len(items) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), "#f4f2ed")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    for position, item in enumerate(items):
        row, column = divmod(position, columns)
        x = column * thumb_w
        y = row * (thumb_h + label_h)
        path = CANDIDATE_DIR / item["file"]
        try:
            with Image.open(path) as image:
                image.thumbnail((thumb_w - 8, thumb_h - 8))
                sheet.paste(image.convert("RGB"), (x + 4, y + 4))
        except OSError:
            draw.rectangle([x + 4, y + 4, x + thumb_w - 4, y + thumb_h - 4], fill="#cccccc")
        draw.text((x + 4, y + thumb_h + 2), f"#{item['index']:03d} {category}", fill="#222222", font=font)
        draw.text((x + 4, y + thumb_h + 16), item["licence"][:26], fill="#555555", font=font)
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    path = SHEET_DIR / f"{category}-{part}.jpg"
    sheet.save(path, quality=88)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Ignore the cached manifest.")
    args = parser.parse_args()

    QA_DIR.mkdir(parents=True, exist_ok=True)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    SHEET_DIR.mkdir(parents=True, exist_ok=True)

    if MANIFEST.exists() and not args.refresh:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        manifest = {"categories": {}}

    for category, queries in CATEGORIES.items():
        if category in manifest["categories"] and not args.refresh:
            continue
        seen: set[str] = set()
        items: list[dict] = []
        scoped_queries: list[str] = []
        for query in queries:
            scoped_queries.extend(
                (
                    query,
                    f"{query} incategory:CC-BY-4.0",
                    f"{query} incategory:CC-Zero",
                )
            )
        for query in scoped_queries:
            for result in search(query):
                if result["title"] in seen:
                    continue
                seen.add(result["title"])
                result["query"] = query
                items.append(result)
            time.sleep(0.2)
        items = items[:72]

        for index, item in enumerate(items, start=1):
            item["index"] = index
            item["file"] = f"{_safe_name(index, item['title'])}.jpg"
            destination = CANDIDATE_DIR / item["file"]
            if not destination.exists():
                try:
                    destination.write_bytes(_get(item["thumb_url"]))
                except (urllib.error.URLError, TimeoutError):
                    item["download_failed"] = True

        manifest["categories"][category] = items
        print(f"{category}: {len(items)} candidates")

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    for category, items in manifest["categories"].items():
        usable = [item for item in items if not item.get("download_failed")]
        for chunk_start in range(0, len(usable), 24):
            chunk = usable[chunk_start : chunk_start + 24]
            if not chunk:
                continue
            part = chunk_start // 24 + 1
            path = _contact_sheet(category, chunk, part)
            print(f"sheet: {path} ({chunk_start + 1}-{chunk_start + len(chunk)})")


if __name__ == "__main__":
    main()
