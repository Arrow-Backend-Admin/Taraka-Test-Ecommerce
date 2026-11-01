#!/usr/bin/env python3
"""Build the Phase 4 placeholder image set, metadata and credits.

The six source photographs are CC0 1.0 or CC BY 4.0 images from Wikimedia
Commons. They are downloaded once, centre-cropped to 4:5, optimised, and copied
to a model/role filename under the storefront's public directory. No image is
hotlinked at runtime.

Usage:
    python brand/phase-4/build_placeholders.py
    python brand/phase-4/build_placeholders.py --source-dir path/to/cache
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = Path(__file__).with_name("placeholder-sources.json")
CATALOGUE_PATH = ROOT / "brand" / "phase-3" / "products.json"
OUTPUT_DIR = ROOT / "apps" / "storefront" / "public" / "placeholders"
METADATA_PATH = Path(__file__).with_name("placeholder-images.json")
CREDITS_PATH = Path(__file__).with_name("image-credits.md")
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
PLACEHOLDER_NOTICE = "Placeholder image, not the actual product"
USAGE = "Storefront placeholder only; never use in ads, social posts or packaging."
DERIVATIVE = "Centre-cropped to 4:5, resized to 800x1000, JPEG quality 80."
TARGET_SIZE = (800, 1000)
USER_AGENT = "santvana-placeholder-builder/1.0 (concept storefront; local build)"
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
        _download(source["download_url"], cache_file)
    image = Image.open(cache_file).convert("RGB")
    return ImageOps.fit(
        image,
        TARGET_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def _image_metadata(
    *,
    product: dict[str, Any],
    role: str,
    filename: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    return {
        "role": role,
        "role_label": ROLE_LABELS[role],
        "filename": filename,
        "url": f"/placeholders/{filename}",
        "storage_key": f"placeholders/{filename}",
        "aspect": "4:5",
        "width": TARGET_SIZE[0],
        "height": TARGET_SIZE[1],
        "alt": source["alt"],
        "is_placeholder": True,
        "placeholder_notice": PLACEHOLDER_NOTICE,
        "usage": USAGE,
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
    }


def _write_credits(metadata: dict[str, Any]) -> None:
    sources = metadata["sources"]
    products = metadata["products"]

    lines = [
        "# Placeholder image credits — Phase 4 Milestone 1",
        "",
        f"Generated from `placeholder-images.json` on {metadata['generated_at']}.",
        "",
        "These are temporary concept placeholders, not product photography. Every",
        "image is marked `is_placeholder=true`. The same six source photographs are",
        "reused across the 30 concept products so no placeholder implies a real",
        "product shot. The images are stored locally as 4:5 derivatives; nothing is",
        "hotlinked. They must never be used in ads, social posts or packaging.",
        "",
        "Selection rule: Wikimedia Commons only, CC0 1.0 or CC BY 4.0. No NC, ND or",
        "SA licences. Source metadata describes plain footwear and feet with no",
        "identifiable faces. A human visual QA pass for third-party marks,",
        "ground-in-frame and overcast light is still required before external use.",
        "",
        "## Sources",
        "",
        "| Source | Photographer | Licence | Licence URL | Source URL | Retrieved |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for source in sources:
        lines.append(
            "| {title} | {photographer} | {licence} | {licence_url} | {source_url} | {retrieved} |".format(
                title=source["source_title"],
                photographer=source["photographer"],
                licence=source["licence_name"],
                licence_url=source["licence_url"],
                source_url=source["source_url"],
                retrieved=source["retrieved_at"],
            )
        )

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Product | Role | Source | Photographer | Licence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for product_slug, product in products.items():
        for image in product["images"]:
            lines.append(
                "| `{filename}` | {product} | {role} | {source} | {photographer} | {licence} |".format(
                    filename=image["filename"],
                    product=product["name"],
                    role=image["role_label"],
                    source=image["source_title"],
                    photographer=image["photographer"],
                    licence=image["licence_name"],
                )
            )

    lines.extend(
        [
            "",
            "## Attribution text",
            "",
            "For any CC BY 4.0 image, keep the photographer, licence and source URL with",
            "the file. The per-file JSON records the full attribution string. The",
            "storefront also shows “Placeholder image, not the actual product” on every",
            "placeholder.",
            "",
        ]
    )
    CREDITS_PATH.write_text("\n".join(lines), encoding="utf-8")


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
    sources = sources_payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit(f"No sources found in {SOURCES_PATH}")

    by_role = {source["role"]: source for source in sources}
    if set(by_role) != set(ROLE_ORDER):
        raise SystemExit(
            f"Expected one source per role {ROLE_ORDER}, found {sorted(by_role)}"
        )
    for source in sources:
        if source["licence_name"] not in ALLOWED_LICENCES:
            raise SystemExit(
                f"Disallowed licence {source['licence_name']} for {source['source_title']}"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prepared = {
        role: _source_image(by_role[role], args.source_dir) for role in ROLE_ORDER
    }

    metadata_products: dict[str, Any] = {}
    written = 0
    for product in products:
        slug = product["slug"]
        images = []
        for role in ROLE_ORDER:
            filename = f"placeholder_{slug}_{role}_4x5_v00.jpg"
            destination = OUTPUT_DIR / filename
            if args.force or not destination.exists():
                prepared[role].save(
                    destination,
                    "JPEG",
                    quality=80,
                    optimize=True,
                    progressive=True,
                )
                written += 1
            images.append(
                _image_metadata(
                    product=product,
                    role=role,
                    filename=filename,
                    source=by_role[role],
                )
            )
        metadata_products[slug] = {
            "name": product["name"],
            "model_code": product.get("model_code"),
            "category": product.get("category"),
            "images": images,
        }

    metadata = {
        "schema_version": 1,
        "generated_at": sources_payload.get("generated_at", "2026-10-31"),
        "notice": PLACEHOLDER_NOTICE,
        "usage": USAGE,
        "source_policy": sources_payload.get("source_policy"),
        "roles": [
            {"role": role, "label": ROLE_LABELS[role]} for role in ROLE_ORDER
        ],
        "sources": sources,
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
    print(f"New derivatives written: {written}")
    print(f"Metadata: {METADATA_PATH}")
    print(f"Credits: {CREDITS_PATH}")
    print(f"Public files: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
