"""Third-round curation probe for sneaker and running roles."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "qa" / "extras2"
MANIFEST = ROOT / "qa" / "extras2.json"
USER_AGENT = "SantvanaPlaceholderCuration/1.0 (concept project)"

PICKS: dict[str, dict[str, str]] = {
    "sneakers": {
        "hero-45": "File:Sneaker.png",
        "lateral": "File:Sneaks1 (Unsplash).jpg",
        "top-down": "File:Sneakers on black cubes (Unsplash).jpg",
        "heel": "File:Houston sneakers (Unsplash).jpg",
    },
    "running": {
        "hero-45": "File:Running shoes (Unsplash).jpg",
        "lateral": "File:Jogging shoes (Unsplash).jpg",
        "on-foot": "File:Berrien Springs sneaker jumps (Unsplash).jpg",
        "top-down": "File:Marathon shoes (Unsplash).jpg",
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
        if not (licence.lower() == "cc0" or licence.lower().startswith("cc by")):
            return None
        return {
            "title": page.get("title", title),
            "licence_name": licence,
            "licence_url": _strip(metadata.get("LicenseUrl", {}).get("value")),
            "photographer": _strip(metadata.get("Artist", {}).get("value")),
            "description": _strip(metadata.get("ImageDescription", {}).get("value")),
            "source_url": "https://commons.wikimedia.org/wiki/"
            + urllib.parse.quote(page.get("title", title).replace(" ", "_")),
            "download_url": info.get("url"),
            "preview_url": info.get("thumburl"),
            "width": info.get("width"),
            "height": info.get("height"),
        }
    return None


def main() -> None:
    records: list[dict] = []
    missing: list[str] = []
    for category, roles in PICKS.items():
        for role, title in roles.items():
            resolved = resolve(title)
            if resolved is None:
                missing.append(f"{category}/{role}: {title}")
                continue
            destination = OUT_DIR / category / f"{role}.jpg"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                try:
                    destination.write_bytes(_get(resolved["preview_url"]))
                except (urllib.error.URLError, TimeoutError) as exc:
                    missing.append(f"{category}/{role}: download failed ({exc})")
                    continue
            records.append({"category": category, "role": role, **resolved})
            time.sleep(1.0)

    MANIFEST.write_text(
        json.dumps({"sources": records, "missing": missing}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"resolved {len(records)} extras2; {len(missing)} missing")
    for item in missing:
        print("  missing:", item)


if __name__ == "__main__":
    main()
