#!/usr/bin/env python3
"""Build the Phase 4 placeholder image set, metadata and credits.

Every category/role slot is either a reviewed CC0 / CC BY Wikimedia Commons
photograph or a neutral grey 4:5 "Image coming" block. Photographs are
centre-cropped to 4:5 and resized; grey blocks are generated. Nothing is
hotlinked at runtime.

Usage:
    python brand/phase-4/build_placeholders.py
    python brand/phase-4/build_placeholders.py --force
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = Path(__file__).with_name("placeholder-sources.json")
CATALOGUE_PATH = ROOT / "brand" / "phase-3" / "products.json"
OUTPUT_DIR = ROOT / "apps" / "storefront" / "public" / "placeholders"
METADATA_PATH = Path(__file__).with_name("placeholder-images.json")
CREDITS_PATH = Path(__file__).with_name("image-credits.md")
CREDITS_JSON_PATH = ROOT / "apps" / "storefront" / "app" / "credits" / "credits.json"
DEFAULT_SOURCE_DIR = Path(__file__).with_name("source-images")

ROLE_ORDER = [
    "hero-45",
    "lateral",
    "heel",
    "top-down",
    "sole-macro",
    "on-foot",
]
ROLE_LABELS = {
    "hero-45": "Hero, 45 degrees",
    "lateral": "Lateral",
    "heel": "Heel",
    "top-down": "Top-down",
    "sole-macro": "Sole macro",
    "on-foot": "On foot",
}
CATEGORY_ORDER = ["sneakers", "running", "sandals", "boots", "everyday"]
PLACEHOLDER_NOTICE = "Placeholder image, not the actual product"
USAGE = "Storefront placeholder only; never use in ads, social posts or packaging."
PHOTO_CHANGE = "Cropped and resized"
GREY_CHANGE = "Generated neutral block"
DERIVATIVE = "Centre-cropped to 4:5, resized to 800x1000, JPEG quality 80."
TARGET_SIZE = (800, 1000)
GREY = (227, 225, 220)
GREY_INK = (122, 119, 114)
USER_AGENT = "santvana-placeholder-builder/2.0 (concept storefront; local build)"
ALLOWED_LICENCES = {"CC0 1.0", "CC BY 4.0"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
            if not data:
                raise ValueError(f"Empty response for {url}")
            destination.write_bytes(data)
            return
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            if attempt == 3:
                raise RuntimeError(f"Could not download {url}") from exc
            time.sleep(10 * (attempt + 1))


def _source_image(source: dict[str, Any], source_dir: Path) -> Image.Image:
    cache_file = source_dir / source["cache_file"]
    if not cache_file.exists():
        url = source.get("download_url") or source.get("preview_url")
        if not url:
            raise RuntimeError(f"No download URL for {source['category']}/{source['role']}")
        _download(url, cache_file)
    with Image.open(cache_file) as image:
        return ImageOps.fit(
            image.convert("RGB"),
            TARGET_SIZE,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )


def _grey_image() -> Image.Image:
    image = Image.new("RGB", TARGET_SIZE, GREY)
    draw = ImageDraw.Draw(image)
    try:
        large = ImageFont.truetype("arial.ttf", 46)
        small = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        large = ImageFont.load_default()
        small = ImageFont.load_default()
    label = "Image coming"
    box = draw.textbbox((0, 0), label, font=large)
    draw.text(
        ((TARGET_SIZE[0] - (box[2] - box[0])) / 2, TARGET_SIZE[1] / 2 - 40),
        label,
        fill=GREY_INK,
        font=large,
    )
    sub = "Placeholder, not the actual product"
    sub_box = draw.textbbox((0, 0), sub, font=small)
    draw.text(
        ((TARGET_SIZE[0] - (sub_box[2] - sub_box[0])) / 2, TARGET_SIZE[1] / 2 + 30),
        sub,
        fill=GREY_INK,
        font=small,
    )
    draw.rectangle([0, 0, TARGET_SIZE[0] - 1, TARGET_SIZE[1] - 1], outline=(205, 202, 196))
    return image


def _photo_alt(category: str, role: str) -> str:
    return (
        f"Placeholder photograph for {category} footwear, "
        f"{ROLE_LABELS[role].lower()} view. Not the actual product."
    )


def _grey_alt(category: str, role: str) -> str:
    return (
        f"Image coming. Neutral placeholder for {category} footwear, "
        f"{ROLE_LABELS[role].lower()} view."
    )


def _image_metadata(
    *,
    category: str,
    role: str,
    filename: str,
    source: dict[str, Any] | None,
    grey: dict[str, Any] | None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "role": role,
        "role_label": ROLE_LABELS[role],
        "filename": filename,
        "url": f"/placeholders/{filename}",
        "storage_key": f"placeholders/{filename}",
        "aspect": "4:5",
        "width": TARGET_SIZE[0],
        "height": TARGET_SIZE[1],
        "is_placeholder": True,
        "placeholder_notice": PLACEHOLDER_NOTICE,
        "usage": USAGE,
        "category": category,
    }
    if source is not None:
        base.update(
            {
                "kind": "photo",
                "alt": _photo_alt(category, role),
                "changes": PHOTO_CHANGE,
                "source": source["source"],
                "source_title": source["source_title"],
                "source_url": source["source_url"],
                "source_description": source["source_description"],
                "download_url": source["download_url"],
                "photographer": source["photographer"],
                "licence_name": source["licence_name"],
                "licence_url": source["licence_url"],
                "licence_version": source["licence_version"],
                "retrieved_at": source["retrieved_at"],
                "attribution": source["attribution"],
                "derivative": DERIVATIVE,
                "qa": source["qa"],
            }
        )
    else:
        assert grey is not None
        base.update(
            {
                "kind": "image_coming",
                "alt": _grey_alt(category, role),
                "changes": GREY_CHANGE,
                "source": None,
                "source_title": None,
                "source_url": None,
                "source_description": None,
                "download_url": None,
                "photographer": None,
                "licence_name": None,
                "licence_url": None,
                "licence_version": None,
                "retrieved_at": None,
                "attribution": None,
                "derivative": "Generated 800x1000 neutral grey block with the label Image coming.",
                "qa": grey["qa"],
                "image_coming_reason": grey["reason"],
            }
        )
    return base


def _write_credits(metadata: dict[str, Any]) -> None:
    sources = metadata["sources"]
    grey = metadata["grey"]
    products = metadata["products"]

    lines = [
        "# Placeholder image credits — Phase 4 Milestone 2",
        "",
        f"Generated from `placeholder-images.json` on {metadata['generated_at']}.",
        "",
        "These are temporary concept placeholders, not product photography. Every",
        "image is marked `is_placeholder=true`. They must never be used in ads,",
        "social posts or packaging.",
        "",
        "Selection rule: Wikimedia Commons only, CC0 1.0 or CC BY 4.0. No NC, ND or",
        "SA licences. Every source photograph was reviewed for third-party marks,",
        "wordmarks, branded silhouettes and identifiable faces. A role with no",
        "suitable source uses a neutral grey 4:5 block labelled “Image coming”",
        "rather than a mismatched photograph.",
        "",
        "Change applied to every photograph: **cropped and resized** (centre crop to",
        "4:5, resized to 800×1000, JPEG quality 80). Grey blocks are generated.",
        "",
        "## Visual QA summary",
        "",
        "| Category | Role | Result | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for source in sources:
        lines.append(
            f"| {source['category']} | {source['role']} | pass | {source['qa']['notes']} |"
        )
    for slot in grey:
        lines.append(
            f"| {slot['category']} | {slot['role']} | no suitable source | {slot['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Sources",
            "",
            "| Category | Role | Source | Photographer | Licence | Licence URL | Source URL | Changes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for source in sources:
        lines.append(
            "| {category} | {role} | {title} | {photographer} | {licence} | {licence_url} | {source_url} | {changes} |".format(
                category=source["category"],
                role=source["role"],
                title=source["source_title"],
                photographer=source["photographer"],
                licence=source["licence_name"],
                licence_url=source["licence_url"],
                source_url=source["source_url"],
                changes=source["changes"],
            )
        )

    lines.extend(
        [
            "",
            "## Grey “Image coming” slots",
            "",
            "| Category | Role | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for slot in grey:
        lines.append(f"| {slot['category']} | {slot['role']} | {slot['reason']} |")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Product | Role | Kind | Source | Photographer | Licence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for product in products.values():
        for image in product["images"]:
            lines.append(
                "| `{filename}` | {product} | {role} | {kind} | {source} | {photographer} | {licence} |".format(
                    filename=image["filename"],
                    product=product["name"],
                    role=image["role_label"],
                    kind=image["kind"],
                    source=image["source_title"] or "—",
                    photographer=image["photographer"] or "—",
                    licence=image["licence_name"] or "—",
                )
            )

    lines.extend(
        [
            "",
            "## Attribution text",
            "",
            "For every CC BY image, keep the photographer, licence and source URL with",
            "the file. The per-file JSON records the full attribution string, and the",
            "product page renders it. The storefront also shows “Placeholder image, not",
            "the actual product” on every placeholder.",
            "",
        ]
    )
    CREDITS_PATH.write_text("\n".join(lines), encoding="utf-8")

    CREDITS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDITS_JSON_PATH.write_text(
        json.dumps(
            {
                "generated_at": metadata["generated_at"],
                "notice": PLACEHOLDER_NOTICE,
                "usage": USAGE,
                "source_policy": metadata["source_policy"],
                "sources": [
                    {
                        key: source[key]
                        for key in (
                            "category",
                            "role",
                            "source_title",
                            "source_url",
                            "photographer",
                            "licence_name",
                            "licence_url",
                            "changes",
                            "attribution",
                            "qa",
                        )
                    }
                    for source in sources
                ],
                "grey": grey,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Cache directory for downloaded source photographs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rewrite derivatives even when the output file already exists.",
    )
    args = parser.parse_args()

    catalogue = _load_json(CATALOGUE_PATH)
    products = catalogue.get("products")
    if not isinstance(products, list) or not products:
        raise SystemExit(f"No products found in {CATALOGUE_PATH}")

    sources_payload = _load_json(SOURCES_PATH)
    sources = sources_payload.get("sources") or []
    grey_slots = sources_payload.get("grey") or []
    if not sources and not grey_slots:
        raise SystemExit(f"No sources found in {SOURCES_PATH}")

    by_slot: dict[tuple[str, str], dict[str, Any]] = {}
    for source in sources:
        if source["licence_name"] not in ALLOWED_LICENCES:
            raise SystemExit(
                f"Disallowed licence {source['licence_name']} for {source['source_title']}"
            )
        by_slot[(source["category"], source["role"])] = source
    grey_by_slot = {(slot["category"], slot["role"]): slot for slot in grey_slots}

    for category in CATEGORY_ORDER:
        for role in ROLE_ORDER:
            key = (category, role)
            if key not in by_slot and key not in grey_by_slot:
                raise SystemExit(f"No source or grey decision for {category}/{role}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prepared = {
        key: _source_image(source, args.source_dir)
        for key, source in by_slot.items()
    }
    grey_image = _grey_image()

    metadata_products: dict[str, Any] = {}
    written = 0
    for product in products:
        slug = product["slug"]
        category = product["category_slug"]
        images = []
        for role in ROLE_ORDER:
            filename = f"placeholder_{slug}_{role}_4x5_v00.jpg"
            destination = OUTPUT_DIR / filename
            source = by_slot.get((category, role))
            if args.force or not destination.exists():
                if source is not None:
                    prepared[(category, role)].save(
                        destination,
                        "JPEG",
                        quality=80,
                        optimize=True,
                        progressive=True,
                    )
                else:
                    grey_image.save(
                        destination,
                        "JPEG",
                        quality=82,
                        optimize=True,
                        progressive=True,
                    )
                written += 1
            images.append(
                _image_metadata(
                    category=category,
                    role=role,
                    filename=filename,
                    source=source,
                    grey=grey_by_slot.get((category, role)),
                )
            )
        metadata_products[slug] = {
            "name": product["name"],
            "model_code": product.get("model_code"),
            "category": product.get("category"),
            "category_slug": category,
            "images": images,
        }

    metadata = {
        "schema_version": 2,
        "generated_at": sources_payload.get("generated_at", "2026-11-02"),
        "notice": PLACEHOLDER_NOTICE,
        "usage": USAGE,
        "source_policy": sources_payload.get("source_policy"),
        "roles": [
            {"role": role, "label": ROLE_LABELS[role]} for role in ROLE_ORDER
        ],
        "sources": sources,
        "grey": grey_slots,
        "product_order": [product["slug"] for product in products],
        "products": metadata_products,
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_credits(metadata)

    print(
        f"Placeholder set: {len(products)} products x {len(ROLE_ORDER)} roles = "
        f"{len(products) * len(ROLE_ORDER)} files."
    )
    print(f"Reviewed photographs: {len(sources)}; grey Image coming slots: {len(grey_slots)}")
    print(f"New derivatives written: {written}")
    print(f"Metadata: {METADATA_PATH}")
    print(f"Credits: {CREDITS_PATH}")
    print(f"Credits JSON: {CREDITS_JSON_PATH}")
    print(f"Public files: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
