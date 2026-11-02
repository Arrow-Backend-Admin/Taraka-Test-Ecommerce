"""Merge the reviewed curation manifests into placeholder-sources.json.

Only sources that passed strict visual QA are kept. Every other category/role
combination is recorded as a grey "Image coming" slot.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = ["sneakers", "running", "sandals", "boots", "everyday"]
ROLES = ["hero-45", "lateral", "heel", "top-down", "sole-macro", "on-foot"]

KEEP = {
    ("sneakers", "on-foot"): ("extras.json", "Plain white canvas sneakers on foot on asphalt; no visible branding or face."),
    ("sandals", "hero-45"): ("curated.json", "Brown strappy sandals, three-quarter front, wood floor, no marks or faces."),
    ("sandals", "lateral"): ("curated.json", "Side profile of brown sandals on foot, soft indoor light, no marks or faces."),
    ("sandals", "top-down"): ("curated.json", "Overhead view of sandals on foot, wood floor, no marks or faces."),
    ("sandals", "on-foot"): ("curated.json", "Sandals worn on foot, floor visible, no marks or faces."),
    ("boots", "hero-45"): ("curated.json", "Brown leather lace-up boots, three-quarter front, wood floor, no marks or faces."),
    ("boots", "lateral"): ("extras.json", "Plain black combat boots in side profile, studio light, no marks or faces."),
    ("boots", "heel"): ("curated.json", "Black boots rear/heel view on rock, soft light, no marks or faces."),
    ("boots", "top-down"): ("curated.json", "Overhead view of boots, plain background, no marks or faces."),
    ("boots", "on-foot"): ("curated.json", "Boots worn on foot, ground visible, no face or marks."),
    ("everyday", "on-foot"): ("curated.json", "Everyday casual shoes worn on feet on pavement, no face or marks."),
    ("everyday", "top-down"): ("extras.json", "Plain maroon espadrille flats, overhead on grass, no marks or faces."),
}

GREY_REASON = {
    ("sneakers", "hero-45"): "Every reviewed sneaker candidate had a brand mark, branded silhouette, overlay or wrong view.",
    ("sneakers", "lateral"): "Every reviewed sneaker candidate had a brand mark, branded silhouette, overlay or wrong view.",
    ("sneakers", "heel"): "Every reviewed sneaker candidate had a brand mark, branded silhouette, overlay or wrong view.",
    ("sneakers", "top-down"): "Every reviewed sneaker candidate had a brand mark, branded silhouette, overlay or wrong view.",
    ("sneakers", "sole-macro"): "No reviewed Commons candidate showed an unbranded sneaker sole close-up.",
    ("running", "hero-45"): "All reviewed running candidates carried a visible Nike, ASICS or Adidas mark.",
    ("running", "lateral"): "All reviewed running candidates carried a visible Nike, ASICS or Adidas mark.",
    ("running", "heel"): "No reviewed Commons candidate showed an unbranded running-shoe heel.",
    ("running", "top-down"): "No reviewed Commons candidate showed an unbranded running-shoe top-down view.",
    ("running", "sole-macro"): "No reviewed Commons candidate showed an unbranded running-shoe sole close-up.",
    ("running", "on-foot"): "All reviewed running candidates carried a visible Nike, ASICS or Adidas mark.",
    ("sandals", "heel"): "The only candidate was an overhead view, not a heel view.",
    ("sandals", "sole-macro"): "No wearable modern sandal sole close-up was available; museum fragments were rejected.",
    ("boots", "sole-macro"): "The only candidate was a front three-quarter view, not a sole close-up.",
    ("everyday", "hero-45"): "Candidates were branded (Sebago), overhead, or the wrong category.",
    ("everyday", "lateral"): "Candidates were overhead, boots, or an illustration rather than a side profile.",
    ("everyday", "heel"): "The only candidate showed boots from the front, not an everyday shoe heel.",
    ("everyday", "sole-macro"): "No unbranded everyday-shoe sole close-up was available.",
}


def _load(name: str) -> dict:
    return json.loads((ROOT / "qa" / name).read_text(encoding="utf-8"))


def main() -> None:
    curated = {(item["category"], item["role"]): item for item in _load("curated.json")["sources"]}
    extras = {(item["category"], item["role"]): item for item in _load("extras.json")["sources"]}

    sources: list[dict] = []
    grey: list[dict] = []
    for category in CATEGORIES:
        for role in ROLES:
            key = (category, role)
            if key in KEEP:
                manifest_name, note = KEEP[key]
                pool = curated if manifest_name == "curated.json" else extras
                record = pool[key]
                licence_raw = record["licence_name"]
                licence = "CC0 1.0" if licence_raw.lower() == "cc0" else licence_raw
                version = "1.0" if licence_raw.lower() == "cc0" else licence.replace("CC BY ", "")
                sources.append(
                    {
                        "category": category,
                        "role": role,
                        "source": "Wikimedia Commons",
                        "source_title": record["title"],
                        "source_url": record["source_url"].replace(
                            "/wiki/File%3A", "/wiki/File:"
                        ),
                        "source_description": record.get("description", ""),
                        "download_url": record["download_url"],
                        "preview_url": record.get("preview_url"),
                        "photographer": record.get("photographer") or "Unknown",
                        "licence_name": licence,
                        "licence_version": version,
                        "licence_url": (
                            record.get("licence_url", "").replace(
                                "http://creativecommons.org/",
                                "https://creativecommons.org/",
                            )
                        ),
                        "retrieved_at": "2026-11-02",
                        "changes": "Cropped and resized",
                        "cache_file": f"{category}-{role}.jpg",
                        "qa": {
                            "reviewed": True,
                            "method": "model visual QA (opencode/nemotron-3.5-super-vl-free)",
                            "result": "pass",
                            "notes": note,
                        },
                        "attribution": (
                            f"{record['title']} by {record.get('photographer') or 'Unknown'}, "
                            f"{licence}, via Wikimedia Commons. Cropped and resized."
                        ),
                    }
                )
            else:
                grey.append(
                    {
                        "category": category,
                        "role": role,
                        "kind": "image_coming",
                        "reason": GREY_REASON[key],
                        "qa": {
                            "reviewed": True,
                            "method": "model visual QA (opencode/nemotron-3.5-super-vl-free)",
                            "result": "no_suitable_source",
                            "notes": GREY_REASON[key],
                        },
                    }
                )

    payload = {
        "schema_version": 2,
        "generated_at": date.today().isoformat(),
        "source_policy": (
            "Wikimedia Commons only. CC0 1.0 or CC BY 4.0. No NC, ND or SA. "
            "Only sources that passed strict visual QA for third-party marks and "
            "identifiable faces are used. Roles without a suitable source use a "
            "neutral grey 'Image coming' block instead of a mismatched photo."
        ),
        "sources": sources,
        "grey": grey,
    }
    (ROOT / "placeholder-sources.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"kept {len(sources)} sources; {len(grey)} grey slots")
    for item in sources:
        print(" ", item["category"], item["role"], item["licence_name"], item["source_title"])


if __name__ == "__main__":
    main()
