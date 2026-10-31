#!/usr/bin/env python3
"""Build the Sāntvana Phase 3 catalogue.

This script is the source of truth for the 30-product concept range. It writes
products.json, products.csv, skus.csv, size-guide.csv, size-guide.md,
pricing-table.md, fields-to-confirm.csv and fields-to-confirm.md.

Product facts are deliberately unconfirmed. Every material, weight, lug depth,
sole compound, fit statement, grip claim and test claim is marked
[TO CONFIRM: manufacturer] unless the founder has supplied it.

Run from the repository root:
    python brand/phase-3/build_catalogue.py
"""

from __future__ import annotations

import csv
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TWO_PLACES = Decimal("0.01")

TO_CONFIRM_MFR = "[TO CONFIRM: manufacturer]"
TO_CONFIRM_CA = "[TO CONFIRM: CA]"
TO_CONFIRM_LAST = "[TO CONFIRM: last]"
TO_CONFIRM_FOUNDER = "[TO CONFIRM: founder]"
TO_CONFIRM_LEGAL = "[TO CONFIRM: legal]"
TO_CONFIRM_3PL = "[TO CONFIRM: 3PL]"
TO_CONFIRM_PHOTO = "[TO CONFIRM: photography]"
TO_CONFIRM_OPS = "[TO CONFIRM: ops]"
TO_CONFIRM_ATTORNEY = "[TO CONFIRM: attorney]"

CONFIRM_RE = re.compile(r"\[TO CONFIRM:\s*([^\]]+)\]")


def q(value: Decimal | int | str) -> Decimal:
    """Round to two decimal places using normal commercial rounding."""
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def money(value: Decimal | int | str) -> float:
    return float(q(value))


def pct(value: Decimal | int | str) -> float:
    return float(q(value))


def money_text(value: Decimal | int | str) -> str:
    return f"{q(value):,.2f}"


def pct_text(value: Decimal | int | str) -> str:
    return f"{q(value):.2f}%"


def owner_of(value: str) -> str:
    match = CONFIRM_RE.search(value)
    return match.group(1).strip() if match else ""


def rupeeize(value: Any) -> Any:
    """Use the rupee sign in generated copy, not the ASCII 'Rs' fallback."""
    if isinstance(value, str):
        return value.replace("Rs ", "₹")
    if isinstance(value, list):
        return [rupeeize(item) for item in value]
    if isinstance(value, dict):
        return {key: rupeeize(item) for key, item in value.items()}
    return value


# UK whole sizes only in v1. EU/US/cm are nominal and must be checked against
# the actual last before publishing. Do not treat these cm values as insole
# lengths or as a fit guarantee.
SIZES: list[dict[str, str]] = [
    {"uk": "3", "eu": "36", "us_men": "4", "us_women": "6", "cm": "22.0"},
    {"uk": "4", "eu": "37", "us_men": "5", "us_women": "7", "cm": "22.9"},
    {"uk": "5", "eu": "38", "us_men": "6", "us_women": "8", "cm": "23.7"},
    {"uk": "6", "eu": "39", "us_men": "7", "us_women": "9", "cm": "24.6"},
    {"uk": "7", "eu": "40", "us_men": "8", "us_women": "10", "cm": "25.4"},
    {"uk": "8", "eu": "41", "us_men": "9", "us_women": "11", "cm": "26.2"},
    {"uk": "9", "eu": "42", "us_men": "10", "us_women": "12", "cm": "27.1"},
    {"uk": "10", "eu": "43", "us_men": "11", "us_women": "13", "cm": "27.9"},
    {"uk": "11", "eu": "44", "us_men": "12", "us_women": "14", "cm": "28.8"},
    {"uk": "12", "eu": "45", "us_men": "13", "us_women": "15", "cm": "29.6"},
    {"uk": "13", "eu": "46", "us_men": "14", "us_women": "16", "cm": "30.5"},
]

CATEGORY_ORDER = ["Sneakers", "Running", "Everyday", "Sandals", "Boots"]
TIER_ORDER = ["good", "better", "best"]

CATEGORIES: dict[str, dict[str, Any]] = {
    "Sneakers": {
        "code": "SN",
        "slug": "sneakers",
        "role": "Traffic driver. The most legible silhouette in the launch range.",
        "season": "All year",
        "hsn_candidates": ["6402", "6403", "6404"],
        "margin_targets": {"good": (48, 51), "better": (50, 53), "best": (52, 55)},
    },
    "Running": {
        "code": "RN",
        "slug": "running",
        "role": "Credibility. The category that carries the fit-and-climate story, once the evidence exists.",
        "season": "All year",
        "hsn_candidates": ["6402", "6403", "6404"],
        "margin_targets": {"good": (46, 49), "better": (48, 51), "best": (51, 54)},
    },
    "Everyday": {
        "code": "EV",
        "slug": "everyday",
        "role": "Volume. The pair bought for the commute, the errand and the weekend.",
        "season": "All year",
        "hsn_candidates": ["6402", "6403", "6404", "6405"],
        "margin_targets": {"good": (52, 55), "better": (51, 54), "best": (54, 57)},
    },
    "Sandals": {
        "code": "SD",
        "slug": "sandals",
        "role": "Summer. The hot-weather entry point and the highest-margin category.",
        "season": "Summer",
        "hsn_candidates": ["6401", "6402", "6405"],
        "margin_targets": {"good": (56, 60), "better": (53, 56), "best": (54, 57)},
    },
    "Boots": {
        "code": "BT",
        "slug": "boots",
        "role": "Halo and outdoor. The lower-volume, higher-price end of the range.",
        "season": "All year",
        "hsn_candidates": ["6401", "6402", "6403", "6404"],
        "margin_targets": {"good": (42, 45), "better": (46, 49), "best": (49, 52)},
    },
}

# 5 categories x 6 products = 30. Each category has 3 good, 2 better, 1 best.
# The ladder deliberately leaves no product between Rs 2,500 and Rs 3,499:
# the 5% / 18% GST line and the two possible threshold interpretations both
# resolve the same way for every product in the range.
PRODUCTS: list[dict[str, Any]] = [
    # Sneakers
    {
        "category": "Sneakers",
        "model_code": "SN-MER",
        "name": "Meridian Low",
        "tier": "good",
        "price": 2299,
        "colour": "Chalk",
        "colour_code": "CHK",
        "colour_hex": "#E9E4D8",
        "cost": 1100,
        "hero": True,
        "silhouette": "low-profile sneaker",
        "description": "A low-profile sneaker in chalk, cut for the commute and the weekend.",
        "hero_reason": "Entry price at the top of the 5% band; the white low-top is the most legible launch silhouette. Planning GM 49.8%.",
    },
    {
        "category": "Sneakers",
        "model_code": "SN-BAS",
        "name": "Baseline",
        "tier": "good",
        "price": 2399,
        "colour": "Ink",
        "colour_code": "INK",
        "colour_hex": "#1C1B19",
        "cost": 1150,
        "hero": False,
        "silhouette": "low-top sneaker",
        "description": "A low-top in ink with a straight, uncluttered line.",
        "hero_reason": None,
    },
    {
        "category": "Sneakers",
        "model_code": "SN-QTR",
        "name": "Quarter",
        "tier": "good",
        "price": 2499,
        "colour": "Clay",
        "colour_code": "CLY",
        "colour_hex": "#A8452B",
        "cost": 1200,
        "hero": False,
        "silhouette": "low-top sneaker",
        "description": "A low-top in clay with a colour-led everyday line.",
        "hero_reason": None,
    },
    {
        "category": "Sneakers",
        "model_code": "SN-CRT",
        "name": "Court",
        "tier": "better",
        "price": 3499,
        "colour": "Bone",
        "colour_code": "BON",
        "colour_hex": "#D8CDBB",
        "cost": 1450,
        "hero": False,
        "silhouette": "court-inspired low-top sneaker",
        "description": "A court-inspired low-top in bone. A quieter shape for the desk-to-dinner end of the week.",
        "hero_reason": None,
    },
    {
        "category": "Sneakers",
        "model_code": "SN-DRF",
        "name": "Drift",
        "tier": "better",
        "price": 3999,
        "colour": "Moss",
        "colour_code": "MOS",
        "colour_hex": "#4A5544",
        "cost": 1650,
        "hero": False,
        "silhouette": "low-top sneaker",
        "description": "A low-top in moss with a softer line. For days that move between office and outside.",
        "hero_reason": None,
    },
    {
        "category": "Sneakers",
        "model_code": "SN-ATL",
        "name": "Atlas",
        "tier": "best",
        "price": 4999,
        "colour": "Slate",
        "colour_code": "SLT",
        "colour_hex": "#3C4A55",
        "cost": 2000,
        "hero": False,
        "silhouette": "low-top sneaker",
        "description": "The best-tier sneaker in slate. A more considered silhouette for the launch range.",
        "hero_reason": None,
    },
    # Running
    {
        "category": "Running",
        "model_code": "RN-TMP",
        "name": "Tempo",
        "tier": "good",
        "price": 2299,
        "colour": "Ink",
        "colour_code": "INK",
        "colour_hex": "#1C1B19",
        "cost": 1150,
        "hero": True,
        "silhouette": "running shoe",
        "description": "A running shoe in ink for the first 5K and the walk after. No performance claim is made until test data exists.",
        "hero_reason": "Lowest entry price in running; the first step into the fit system. Planning GM 47.5%.",
    },
    {
        "category": "Running",
        "model_code": "RN-STR",
        "name": "Stride",
        "tier": "good",
        "price": 2399,
        "colour": "Chalk",
        "colour_code": "CHK",
        "colour_hex": "#E9E4D8",
        "cost": 1200,
        "hero": False,
        "silhouette": "running shoe",
        "description": "A running shoe in chalk with a clean upper. For the regular short run.",
        "hero_reason": None,
    },
    {
        "category": "Running",
        "model_code": "RN-LOP",
        "name": "Loop",
        "tier": "good",
        "price": 2499,
        "colour": "Clay",
        "colour_code": "CLY",
        "colour_hex": "#A8452B",
        "cost": 1250,
        "hero": False,
        "silhouette": "running shoe",
        "description": "A running shoe in clay for the loop you actually do.",
        "hero_reason": None,
    },
    {
        "category": "Running",
        "model_code": "RN-RLY",
        "name": "Relay",
        "tier": "better",
        "price": 3499,
        "colour": "Moss",
        "colour_code": "MOS",
        "colour_hex": "#4A5544",
        "cost": 1500,
        "hero": False,
        "silhouette": "running shoe",
        "description": "A better-tier running shoe in moss. A more considered shape for weekly mileage.",
        "hero_reason": None,
    },
    {
        "category": "Running",
        "model_code": "RN-PAC",
        "name": "Pace",
        "tier": "better",
        "price": 3999,
        "colour": "Slate",
        "colour_code": "SLT",
        "colour_hex": "#3C4A55",
        "cost": 1700,
        "hero": False,
        "silhouette": "running shoe",
        "description": "A better-tier running shoe in slate. For the run that has a time attached.",
        "hero_reason": None,
    },
    {
        "category": "Running",
        "model_code": "RN-MIL",
        "name": "Mile",
        "tier": "best",
        "price": 4999,
        "colour": "Ground",
        "colour_code": "GRD",
        "colour_hex": "#2B2722",
        "cost": 2000,
        "hero": False,
        "silhouette": "running shoe",
        "description": "The best-tier running shoe in ground. The halo of the running range; no speed, grip or cushioning claim is made until test data exists.",
        "hero_reason": None,
    },
    # Everyday
    {
        "category": "Everyday",
        "model_code": "EV-DLY",
        "name": "Daily",
        "tier": "good",
        "price": 2299,
        "colour": "Chalk",
        "colour_code": "CHK",
        "colour_hex": "#E9E4D8",
        "cost": 1000,
        "hero": True,
        "silhouette": "everyday shoe",
        "description": "An everyday shoe in chalk for the school run, the station and the shop. A simple shape that does not ask for attention.",
        "hero_reason": "Lowest entry price in everyday; highest planning GM in the good tier at 54.3%. The volume driver.",
    },
    {
        "category": "Everyday",
        "model_code": "EV-ERR",
        "name": "Errand",
        "tier": "good",
        "price": 2399,
        "colour": "Sand",
        "colour_code": "SND",
        "colour_hex": "#C9B99F",
        "cost": 1050,
        "hero": False,
        "silhouette": "everyday shoe",
        "description": "An everyday shoe in sand for the short trips that add up.",
        "hero_reason": None,
    },
    {
        "category": "Everyday",
        "model_code": "EV-COM",
        "name": "Commute",
        "tier": "good",
        "price": 2499,
        "colour": "Ink",
        "colour_code": "INK",
        "colour_hex": "#1C1B19",
        "cost": 1100,
        "hero": False,
        "silhouette": "everyday shoe",
        "description": "An everyday shoe in ink for the walk between transport and desk.",
        "hero_reason": None,
    },
    {
        "category": "Everyday",
        "model_code": "EV-MKT",
        "name": "Market",
        "tier": "better",
        "price": 3499,
        "colour": "Bone",
        "colour_code": "BON",
        "colour_hex": "#D8CDBB",
        "cost": 1400,
        "hero": False,
        "silhouette": "everyday shoe",
        "description": "A better-tier everyday shoe in bone. For long days that move between indoors and out.",
        "hero_reason": None,
    },
    {
        "category": "Everyday",
        "model_code": "EV-SUN",
        "name": "Sunday",
        "tier": "better",
        "price": 3999,
        "colour": "Clay",
        "colour_code": "CLY",
        "colour_hex": "#A8452B",
        "cost": 1600,
        "hero": False,
        "silhouette": "everyday shoe",
        "description": "A better-tier everyday shoe in clay. The slower end of the week.",
        "hero_reason": None,
    },
    {
        "category": "Everyday",
        "model_code": "EV-NBR",
        "name": "Neighbour",
        "tier": "best",
        "price": 4999,
        "colour": "Moss",
        "colour_code": "MOS",
        "colour_hex": "#4A5544",
        "cost": 1900,
        "hero": False,
        "silhouette": "everyday shoe",
        "description": "The best-tier everyday shoe in moss. A quieter, more considered everyday shape.",
        "hero_reason": None,
    },
    # Sandals
    {
        "category": "Sandals",
        "model_code": "SD-STEP",
        "name": "Step",
        "tier": "good",
        "price": 2299,
        "colour": "Sand",
        "colour_code": "SND",
        "colour_hex": "#C9B99F",
        "cost": 900,
        "hero": False,
        "silhouette": "sandal",
        "description": "An everyday sandal in sand for the walk to the corner and back.",
        "hero_reason": None,
    },
    {
        "category": "Sandals",
        "model_code": "SD-SLID",
        "name": "Slide",
        "tier": "good",
        "price": 2399,
        "colour": "Ink",
        "colour_code": "INK",
        "colour_hex": "#1C1B19",
        "cost": 950,
        "hero": False,
        "silhouette": "slide",
        "description": "A slide in ink for hot days and short distances.",
        "hero_reason": None,
    },
    {
        "category": "Sandals",
        "model_code": "SD-STRP",
        "name": "Strap",
        "tier": "good",
        "price": 2499,
        "colour": "Clay",
        "colour_code": "CLY",
        "colour_hex": "#A8452B",
        "cost": 1000,
        "hero": False,
        "silhouette": "strap sandal",
        "description": "A strap sandal in clay for the market and the beach road.",
        "hero_reason": None,
    },
    {
        "category": "Sandals",
        "model_code": "SD-SHOR",
        "name": "Shore",
        "tier": "better",
        "price": 3499,
        "colour": "Bone",
        "colour_code": "BON",
        "colour_hex": "#D8CDBB",
        "cost": 1350,
        "hero": False,
        "silhouette": "sandal",
        "description": "A better-tier sandal in bone for the summer weekend.",
        "hero_reason": None,
    },
    {
        "category": "Sandals",
        "model_code": "SD-DUST",
        "name": "Dust",
        "tier": "better",
        "price": 3999,
        "colour": "Moss",
        "colour_code": "MOS",
        "colour_hex": "#4A5544",
        "cost": 1550,
        "hero": False,
        "silhouette": "sandal",
        "description": "A better-tier sandal in moss for city heat.",
        "hero_reason": None,
    },
    {
        "category": "Sandals",
        "model_code": "SD-CTYD",
        "name": "Courtyard",
        "tier": "best",
        "price": 4999,
        "colour": "Slate",
        "colour_code": "SLT",
        "colour_hex": "#3C4A55",
        "cost": 1900,
        "hero": True,
        "silhouette": "sandal",
        "description": "The best-tier sandal in slate. A more finished summer shape.",
        "hero_reason": "Best-tier sandal at Rs 4,999; summer halo and the highest AOV in the category. Planning GM 55.2%.",
    },
    # Boots
    {
        "category": "Boots",
        "model_code": "BT-SITE",
        "name": "Site",
        "tier": "good",
        "price": 2299,
        "colour": "Ground",
        "colour_code": "GRD",
        "colour_hex": "#2B2722",
        "cost": 1250,
        "hero": False,
        "silhouette": "boot",
        "description": "A boot in ground for the site, the field and the walk home. No waterproof or slip claim is made.",
        "hero_reason": None,
    },
    {
        "category": "Boots",
        "model_code": "BT-FLD",
        "name": "Field",
        "tier": "good",
        "price": 2399,
        "colour": "Sand",
        "colour_code": "SND",
        "colour_hex": "#C9B99F",
        "cost": 1300,
        "hero": False,
        "silhouette": "boot",
        "description": "A boot in sand for the edge of the city.",
        "hero_reason": None,
    },
    {
        "category": "Boots",
        "model_code": "BT-FRG",
        "name": "Forge",
        "tier": "good",
        "price": 2499,
        "colour": "Ink",
        "colour_code": "INK",
        "colour_hex": "#1C1B19",
        "cost": 1350,
        "hero": False,
        "silhouette": "boot",
        "description": "A boot in ink with a clean, grounded line. For the days that start early.",
        "hero_reason": None,
    },
    {
        "category": "Boots",
        "model_code": "BT-RDG",
        "name": "Ridge",
        "tier": "better",
        "price": 3499,
        "colour": "Moss",
        "colour_code": "MOS",
        "colour_hex": "#4A5544",
        "cost": 1550,
        "hero": False,
        "silhouette": "boot",
        "description": "A better-tier boot in moss. A more grounded shape for uneven ground; no grip claim is made until test data exists.",
        "hero_reason": None,
    },
    {
        "category": "Boots",
        "model_code": "BT-QRY",
        "name": "Quarry",
        "tier": "better",
        "price": 3999,
        "colour": "Slate",
        "colour_code": "SLT",
        "colour_hex": "#3C4A55",
        "cost": 1750,
        "hero": False,
        "silhouette": "boot",
        "description": "A better-tier boot in slate. For the long way home.",
        "hero_reason": None,
    },
    {
        "category": "Boots",
        "model_code": "BT-HLT",
        "name": "Halt",
        "tier": "best",
        "price": 4999,
        "colour": "Clay",
        "colour_code": "CLY",
        "colour_hex": "#A8452B",
        "cost": 2100,
        "hero": True,
        "silhouette": "boot",
        "description": "The best-tier boot in clay. The halo of the boot range.",
        "hero_reason": "Best-tier boot at Rs 4,999; the outdoor-and-site halo. Planning GM 50.4%.",
    },
]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build_variants(product: dict[str, Any], sku_prefix: str, net: float, rate: float, gm: float, gmp: float) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for size in SIZES:
        variants.append(
            {
                "sku": f"{sku_prefix}-UK{size['uk']}",
                "size_uk": f"UK {size['uk']}",
                "size_eu": f"EU {size['eu']}",
                "size_us_men": f"US {size['us_men']}",
                "size_us_women": f"US {size['us_women']}",
                "foot_length_cm": size["cm"],
                "foot_length_cm_status": TO_CONFIRM_LAST,
                "price_inr": product["price_inr"],
                "gst_rate": rate,
                "net_revenue_inr": net,
                "target_landed_cost_inr": product["target_landed_cost_inr"],
                "gross_margin_inr": gm,
                "gross_margin_pct": gmp,
                "stock_status": "not_allocated",
            }
        )
    return variants


def build_images(product: dict[str, Any], slug: str) -> list[dict[str, str]]:
    roles = [
        ("hero-45", f"The {product['name']} in {product['colour']}, a {product['silhouette']}, on concrete at a low three-quarter angle."),
        ("side-profile", f"Side profile of the {product['name']} in {product['colour']}."),
        ("sole-macro", f"Sole detail of the {product['name']} in {product['colour']}."),
        ("on-foot-34", f"The {product['name']} in {product['colour']} worn on a city pavement, three-quarter view."),
    ]
    images: list[dict[str, str]] = []
    for role, alt in roles:
        filename = f"drop-01_{slug}_{role}_4x5_v01.jpg"
        images.append(
            {
                "role": role,
                "filename": filename,
                "storage_key": f"brand/drop-01/{filename}",
                "aspect": "4:5",
                "alt": alt,
                "status": "brief only; no asset",
            }
        )
    return images


def build_product(definition: dict[str, Any]) -> dict[str, Any]:
    category = definition["category"]
    config = CATEGORIES[category]
    tier = definition["tier"]
    price = definition["price"]
    rate = 0.05 if price <= 2500 else 0.18
    net = money(Decimal(price) / (Decimal("1") + Decimal(str(rate))))
    gst_amount = money(Decimal(price) - Decimal(str(net)))
    cost = definition["cost"]
    gm = money(Decimal(str(net)) - Decimal(cost))
    gmp = pct(Decimal(str(gm)) / Decimal(str(net)) * Decimal("100"))
    low, high = config["margin_targets"][tier]
    slug = f"{slugify(definition['name'])}-{slugify(definition['colour'])}"
    sku_prefix = f"{definition['model_code']}-{definition['colour_code']}"
    product_id = sku_prefix
    discount_threshold = None
    if price > 2500:
        discount_threshold = pct((Decimal("1") - Decimal("2500") / Decimal(price)) * Decimal("100"))
        discount_note = (
            f"A discount of about {discount_threshold:.2f}% or more takes the invoice to Rs 2,500 or below; "
            "the 5% rate may then apply. The exact treatment is [TO CONFIRM: CA]."
        )
    else:
        discount_note = (
            "At or below Rs 2,500. A discount stays in the 5% band; a price increase above "
            "Rs 2,500 flips to 18%."
        )

    product: dict[str, Any] = {
        "product_id": product_id,
        "sku_prefix": sku_prefix,
        "sku_pattern": "MODEL-COLOUR-SIZE",
        "name": definition["name"],
        "slug": slug,
        "category": category,
        "category_code": config["code"],
        "category_slug": config["slug"],
        "tier": tier,
        "tier_label": tier.title(),
        "model_code": definition["model_code"],
        "colour": definition["colour"],
        "colour_code": definition["colour_code"],
        "colour_hex": definition["colour_hex"],
        "silhouette": definition["silhouette"],
        "gender": "Unisex",
        "age_group": "Adult",
        "season": config["season"],
        "drop": "Drop 01",
        "launch_date": TO_CONFIRM_FOUNDER,
        "status": "concept",
        "name_status": "concept label; not trademark cleared",
        "price_inr": price,
        "mrp_inr": price,
        "price_basis": "GST-inclusive MRP",
        "gst_rate": rate,
        "gst_rate_pct": 5 if rate == 0.05 else 18,
        "gst_bucket": "at_or_below_2500" if price <= 2500 else "above_2500",
        "gst_amount_inr": gst_amount,
        "net_revenue_inr": net,
        "target_landed_cost_inr": cost,
        "cost_basis": "planning assumption; not a supplier quote",
        "gross_margin_inr": gm,
        "gross_margin_pct": gmp,
        "margin_target_low_pct": low,
        "margin_target_high_pct": high,
        "margin_target_pct": f"{low}–{high}%",
        "discount_flip_threshold_pct": discount_threshold,
        "discount_flip_note": discount_note,
        "size_run": "UK 3-13",
        "size_system": "UK whole sizes only in v1",
        "sku_count": len(SIZES),
        "hero": definition["hero"],
        "hero_reason": definition["hero_reason"],
        "restock_priority": "A" if definition["hero"] else ("B" if tier in ("better", "best") else "C"),
        "short_description": definition["description"],
        "long_description": (
            f"{definition['description']} The final last, upper, sole and weight are pending "
            "manufacturer confirmation; no fit, grip or test claim is made in this concept record."
        ),
        "features": [
            f"{definition['silhouette'][0].upper() + definition['silhouette'][1:]} silhouette",
            f"Colour: {definition['colour']}",
            "Sizes UK 3-13",
            "Free size exchange twice",
            "30-day returns from delivery",
            f"Construction and materials: {TO_CONFIRM_MFR}",
        ],
        "tags": [
            config["slug"],
            tier,
            slugify(definition["colour"]),
            slugify(config["season"]),
            "drop-01",
        ],
        "seo_title": f"{definition['name']} - {definition['colour']} | Sāntvana",
        "seo_description": (
            f"{definition['description']} Fit, materials and weight are pending manufacturer "
            "confirmation. Free size exchange twice; 30-day returns from delivery."
        ),
        "manufacturer": TO_CONFIRM_MFR,
        "country_of_origin": TO_CONFIRM_MFR,
        "upper_material": TO_CONFIRM_MFR,
        "lining_material": TO_CONFIRM_MFR,
        "insole_material": TO_CONFIRM_MFR,
        "midsole_material": TO_CONFIRM_MFR,
        "outsole_material": TO_CONFIRM_MFR,
        "sole_compound": TO_CONFIRM_MFR,
        "weight_g": TO_CONFIRM_MFR,
        "lug_depth_mm": TO_CONFIRM_MFR,
        "drop_mm": TO_CONFIRM_MFR,
        "closure": TO_CONFIRM_MFR,
        "heel_height_mm": TO_CONFIRM_MFR,
        "toe_shape": TO_CONFIRM_MFR,
        "last_width": TO_CONFIRM_MFR,
        "water_resistance": TO_CONFIRM_MFR,
        "fit_note": TO_CONFIRM_MFR,
        "fit_recommendation": TO_CONFIRM_MFR,
        "grip_claim": TO_CONFIRM_MFR,
        "test_claim": TO_CONFIRM_MFR,
        "care": TO_CONFIRM_MFR,
        "hsn": TO_CONFIRM_CA,
        "hsn_candidates": config["hsn_candidates"],
        "legal_metrology": TO_CONFIRM_LEGAL,
        "performance_claims": [],
        "claims": [
            {
                "claim": "Free size exchange twice",
                "status": "confirmed policy",
                "evidence": "../strategy.md §6",
            },
            {
                "claim": "30-day returns from delivery",
                "status": "confirmed policy",
                "evidence": "../strategy.md §6",
            },
        ],
        "images": build_images(definition, slug),
    }
    product["variants"] = build_variants(product, sku_prefix, net, rate, gm, gmp)
    return product


def build_payload() -> dict[str, Any]:
    products = [build_product(definition) for definition in PRODUCTS]
    bucket_counts = {
        "at_or_below_2500": sum(1 for p in products if p["gst_bucket"] == "at_or_below_2500"),
        "above_2500": sum(1 for p in products if p["gst_bucket"] == "above_2500"),
    }
    tier_counts = {tier: sum(1 for p in products if p["tier"] == tier) for tier in TIER_ORDER}
    sku_count = sum(len(p["variants"]) for p in products)
    return {
        "schema_version": "1.0.0",
        "generated_at": "2026-10-31",
        "brand": "Sāntvana",
        "status": "concept - product facts unconfirmed; not for production",
        "currency": "INR",
        "market": "India only",
        "price_band_inr": [min(p["price_inr"] for p in products), max(p["price_inr"] for p in products)],
        "core_price_band_inr": [2299, 4999],
        "catalogue": {
            "products": len(products),
            "categories": len(CATEGORY_ORDER),
            "products_per_category": 6,
            "tiers": tier_counts,
            "gst_buckets": bucket_counts,
            "skus": sku_count,
            "sizes_per_product": len(SIZES),
        },
        "gst_rule": {
            "source": "Notification 9/2025-Central Tax (Rate), effective 22 September 2025 (founder-supplied)",
            "headings": ["6401", "6402", "6403", "6404", "6405"],
            "threshold_inr_per_pair": 2500,
            "rates": {"at_or_below_2500": 0.05, "above_2500": 0.18},
            "basis": "invoice sale value, whole pair",
            "threshold_basis": TO_CONFIRM_CA,
            "ca_confirmation": "A chartered accountant must confirm whether the Rs 2,500 threshold is measured before or after tax.",
            "discount_flip": "Discounts can move a pair across the threshold and change the rate. [TO CONFIRM: CA]",
        },
        "size_system": {
            "uk_range": "UK 3-13",
            "whole_sizes_only": True,
            "half_sizes": TO_CONFIRM_MFR,
            "width": TO_CONFIRM_MFR,
            "cm_basis": "foot length, not insole length",
            "cm_status": TO_CONFIRM_LAST,
            "rows": SIZES,
        },
        "image_convention": {
            "pattern": "drop-01_<product-slug>_<role>_4x5_v01.jpg",
            "aspect": "4:5",
            "roles": ["hero-45", "side-profile", "sole-macro", "on-foot-34"],
            "storage": "Cloudflare R2 under brand/drop-01/",
            "status": "brief only; no assets",
            "credit": TO_CONFIRM_PHOTO,
            "release": TO_CONFIRM_LEGAL,
        },
        "claims_register": {
            "source": "../strategy.md §7",
            "confirmed": ["Free size exchange twice", "30-day returns from delivery"],
            "banned_in_v1": [
                "vegan",
                "recycled",
                "sustainable",
                "slip-proof",
                "tested on wet tile",
                "fits Indian feet",
                "grip that grips wet tile",
            ],
            "rule": "No performance, material or fit claim ships without the evidence column filled.",
        },
        "placeholders_not_used": [
            "268 g (sample copy placeholder; not carried into the catalogue)",
            "4 mm lugs (sample copy placeholder; not carried into the catalogue)",
        ],
        "notes": (
            "All product facts marked [TO CONFIRM: manufacturer] are not supplied. Model names "
            "are concept labels, not trademark cleared. Costs and margins are planning "
            "assumptions, not supplier quotes."
        ),
        "products": products,
    }


PRODUCT_CSV_COLUMNS = [
    "product_id",
    "sku_prefix",
    "sku_pattern",
    "name",
    "slug",
    "category",
    "category_slug",
    "tier",
    "tier_label",
    "model_code",
    "colour",
    "colour_code",
    "colour_hex",
    "silhouette",
    "gender",
    "age_group",
    "season",
    "drop",
    "launch_date",
    "status",
    "name_status",
    "price_inr",
    "mrp_inr",
    "price_basis",
    "gst_rate",
    "gst_rate_pct",
    "gst_bucket",
    "gst_amount_inr",
    "net_revenue_inr",
    "target_landed_cost_inr",
    "cost_basis",
    "gross_margin_inr",
    "gross_margin_pct",
    "margin_target_low_pct",
    "margin_target_high_pct",
    "margin_target_pct",
    "discount_flip_threshold_pct",
    "discount_flip_note",
    "size_run",
    "size_system",
    "sku_count",
    "hero",
    "hero_reason",
    "restock_priority",
    "short_description",
    "long_description",
    "features",
    "tags",
    "seo_title",
    "seo_description",
    "manufacturer",
    "country_of_origin",
    "upper_material",
    "lining_material",
    "insole_material",
    "midsole_material",
    "outsole_material",
    "sole_compound",
    "weight_g",
    "lug_depth_mm",
    "drop_mm",
    "closure",
    "heel_height_mm",
    "toe_shape",
    "last_width",
    "water_resistance",
    "fit_note",
    "fit_recommendation",
    "grip_claim",
    "test_claim",
    "care",
    "hsn",
    "hsn_candidates",
    "legal_metrology",
    "image_hero",
    "image_side",
    "image_sole",
    "image_on_foot",
    "image_status",
    "confirmed_claims",
]


def product_csv_row(product: dict[str, Any]) -> dict[str, Any]:
    images = {image["role"]: image for image in product["images"]}
    row: dict[str, Any] = {}
    for column in PRODUCT_CSV_COLUMNS:
        if column == "features":
            value: Any = "; ".join(product["features"])
        elif column == "tags":
            value = "; ".join(product["tags"])
        elif column == "hsn_candidates":
            value = "; ".join(product["hsn_candidates"])
        elif column == "confirmed_claims":
            value = "; ".join(claim["claim"] for claim in product["claims"])
        elif column == "image_hero":
            value = images["hero-45"]["filename"]
        elif column == "image_side":
            value = images["side-profile"]["filename"]
        elif column == "image_sole":
            value = images["sole-macro"]["filename"]
        elif column == "image_on_foot":
            value = images["on-foot-34"]["filename"]
        elif column == "image_status":
            value = "brief only; no asset"
        else:
            value = product.get(column, "")
        if isinstance(value, bool):
            value = "true" if value else "false"
        if value is None:
            value = ""
        row[column] = value
    return row


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_products_csv(products: list[dict[str, Any]]) -> None:
    write_csv(ROOT / "products.csv", PRODUCT_CSV_COLUMNS, [product_csv_row(p) for p in products])


def write_skus_csv(products: list[dict[str, Any]]) -> None:
    columns = [
        "sku",
        "product_id",
        "product_name",
        "category",
        "tier",
        "model_code",
        "colour_code",
        "size_uk",
        "size_eu",
        "size_us_men",
        "size_us_women",
        "foot_length_cm",
        "foot_length_cm_status",
        "price_inr",
        "gst_rate",
        "net_revenue_inr",
        "target_landed_cost_inr",
        "gross_margin_inr",
        "gross_margin_pct",
        "stock_status",
    ]
    rows: list[dict[str, Any]] = []
    for product in products:
        for variant in product["variants"]:
            rows.append(
                {
                    "sku": variant["sku"],
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "category": product["category"],
                    "tier": product["tier"],
                    "model_code": product["model_code"],
                    "colour_code": product["colour_code"],
                    "size_uk": variant["size_uk"],
                    "size_eu": variant["size_eu"],
                    "size_us_men": variant["size_us_men"],
                    "size_us_women": variant["size_us_women"],
                    "foot_length_cm": variant["foot_length_cm"],
                    "foot_length_cm_status": variant["foot_length_cm_status"],
                    "price_inr": variant["price_inr"],
                    "gst_rate": variant["gst_rate"],
                    "net_revenue_inr": variant["net_revenue_inr"],
                    "target_landed_cost_inr": variant["target_landed_cost_inr"],
                    "gross_margin_inr": variant["gross_margin_inr"],
                    "gross_margin_pct": variant["gross_margin_pct"],
                    "stock_status": variant["stock_status"],
                }
            )
    write_csv(ROOT / "skus.csv", columns, rows)


def write_size_guide_csv() -> None:
    columns = [
        "size_uk",
        "size_eu",
        "size_us_men",
        "size_us_women",
        "foot_length_cm",
        "cm_status",
        "half_sizes",
        "width",
    ]
    rows = []
    for size in SIZES:
        rows.append(
            {
                "size_uk": f"UK {size['uk']}",
                "size_eu": f"EU {size['eu']}",
                "size_us_men": f"US {size['us_men']}",
                "size_us_women": f"US {size['us_women']}",
                "foot_length_cm": size["cm"],
                "cm_status": TO_CONFIRM_LAST,
                "half_sizes": TO_CONFIRM_MFR,
                "width": TO_CONFIRM_MFR,
            }
        )
    write_csv(ROOT / "size-guide.csv", columns, rows)


def write_size_guide_md() -> None:
    lines = [
        "# Size guide - Sāntvana",
        "",
        "**Phase 3 · 31 October 2026 · concept only**",
        "The size run is UK 3-13, whole sizes only in v1. Every cm value is **nominal foot length**, not insole length, and is **[TO CONFIRM: last]** against the actual last before publishing. Half sizes and width are **[TO CONFIRM: manufacturer]**.",
        "",
        "## Conversion table",
        "",
        "| UK | EU | US Men | US Women | Foot length (cm) | cm status |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for size in SIZES:
        lines.append(
            f"| {size['uk']} | {size['eu']} | {size['us_men']} | {size['us_women']} | {size['cm']} | {TO_CONFIRM_LAST} |"
        )
    lines += [
        "",
        "US Men and US Women are both shown because the launch range is positioned as unisex. Confirm the US conversion with the manufacturer; do not publish a single US column until the last is checked.",
        "",
        "## How to measure",
        "",
        "1. Stand on a sheet of paper with the heel against a wall.",
        "2. Mark the longest toe. Measure heel to mark in centimetres.",
        "3. Measure both feet and use the longer one.",
        "4. Do not add a fixed allowance until the last and the fit trial are confirmed. The allowance is [TO CONFIRM: manufacturer].",
        "",
        "## Fit advice",
        "",
        "- **Do not publish \"true to size\" or \"wide fit\" yet.** The fit statement and width are [TO CONFIRM: manufacturer].",
        "- **Half sizes are not in the v1 size run.** The between-sizes recommendation is [TO CONFIRM: manufacturer].",
        "- **The cm values must be checked against the last.** A conversion table is not a fit guarantee.",
        "- **Exchange policy:** free size exchange twice; 30-day returns from delivery. See `policies.md`.",
        "",
        "## Implementation",
        "",
        "- `size-guide.csv` is the machine-readable version of this table.",
        "- `skus.csv` carries the UK, EU, US Men, US Women and cm values for every SKU.",
        "- The storefront should show the cm status until the last is confirmed; do not hide it behind a tooltip.",
        "",
    ]
    (ROOT / "size-guide.md").write_text("\n".join(lines), encoding="utf-8")


def write_pricing_table(products: list[dict[str, Any]]) -> None:
    lines = [
        "# Per-product net revenue and margin - planning model",
        "",
        "**Phase 3 · 31 October 2026 · concept only**",
        "Prices are GST-inclusive MRP. Net revenue = price / (1 + GST). Gross margin = net revenue - target landed cost. Costs are planning assumptions, not supplier quotes. Gross margin excludes reverse logistics, payment fees, marketing, fulfilment and fixed costs.",
        "",
        "| # | Product | Category | Tier | Price ₹ | GST | GST ₹ | Net ₹ | Landed cost ₹ | GM ₹ | GM % | Target |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for index, product in enumerate(products, start=1):
        lines.append(
            "| {index} | {name} ({colour}) | {category} | {tier} | {price} | {gst} | {gst_amount} | {net} | {cost} | {gm} | {gmp} | {target} |".format(
                index=index,
                name=product["name"],
                colour=product["colour"],
                category=product["category"],
                tier=product["tier_label"],
                price=f"{product['price_inr']:,}",
                gst=f"{product['gst_rate_pct']}%",
                gst_amount=money_text(product["gst_amount_inr"]),
                net=money_text(product["net_revenue_inr"]),
                cost=f"{product['target_landed_cost_inr']:,}",
                gm=money_text(product["gross_margin_inr"]),
                gmp=pct_text(product["gross_margin_pct"]),
                target=product["margin_target_pct"],
            )
        )
    at_or_below = sum(1 for p in products if p["gst_bucket"] == "at_or_below_2500")
    above = sum(1 for p in products if p["gst_bucket"] == "above_2500")
    avg_net = sum(Decimal(str(p["net_revenue_inr"])) for p in products) / len(products)
    avg_gm = sum(Decimal(str(p["gross_margin_inr"])) for p in products) / len(products)
    avg_margin = avg_gm / avg_net * Decimal("100")
    lines += [
        "",
        "## Summary",
        "",
        f"- **{at_or_below} products at or below ₹2,500:** 5% GST.",
        f"- **{above} products above ₹2,500:** 18% GST.",
        f"- **Average net revenue:** ₹{money_text(avg_net)} per product (simple average, not sales-weighted).",
        f"- **Average gross margin:** ₹{money_text(avg_gm)} per product, or {pct_text(avg_margin)}.",
        "- **The margin is a product gross margin, not net profit.** Reverse logistics, payment fees, marketing, fulfilment and fixed costs come out of it.",
        "",
        "## Discount thresholds",
        "",
        "| Full price | 18% band with net ≥ ₹2,380.95 | Avoid: 18% dead zone | 5% rate band (price ≤ ₹2,500) |",
        "|---:|---:|---:|---:|",
        "| ₹3,499 | 0–19.70% | 19.71–28.55% | 28.56%+ |",
        "| ₹3,999 | 0–29.74% | 29.75–37.48% | 37.49%+ |",
        "| ₹4,999 | 0–43.80% | 43.81–49.98% | 49.99%+ |",
        "",
        "A product at ₹2,499 stays in the 5% band under discount. A price increase above ₹2,500 flips it to 18%. Do not discount a product into the ₹2,501–₹2,809.52 dead zone: net revenue falls below the ₹2,500-at-5% case. The exact treatment is [TO CONFIRM: CA].",
        "",
    ]
    (ROOT / "pricing-table.md").write_text("\n".join(lines), encoding="utf-8")


def write_fields_to_confirm(products: list[dict[str, Any]]) -> None:
    field_notes = {
        "manufacturer": "Legal manufacturer name and address for the label.",
        "country_of_origin": "Legal label requirement.",
        "upper_material": "Exact material and composition; no vegan/recycled claim without a certificate.",
        "lining_material": "Exact material and composition.",
        "insole_material": "Exact material and composition.",
        "midsole_material": "Exact material and composition.",
        "outsole_material": "Exact material and composition.",
        "sole_compound": "Exact compound; no grip or durability claim without test data.",
        "weight_g": "The sample copy's 268 g is a placeholder and is not used.",
        "lug_depth_mm": "The sample copy's 4 mm lugs are a placeholder and are not used.",
        "drop_mm": "Heel-to-toe drop; confirm the measurement method.",
        "closure": "Lace, strap or zip type and hardware.",
        "heel_height_mm": "Measured heel height.",
        "toe_shape": "Last and toe shape; confirm before any fit copy.",
        "last_width": "Width and last; do not claim wide fit until measured.",
        "water_resistance": "No waterproof claim without test data.",
        "fit_note": "Do not publish 'true to size' or 'wide fit' until measured.",
        "fit_recommendation": "Do not publish a fit recommendation until the last is checked.",
        "grip_claim": "No grip claim without a test protocol and a result.",
        "test_claim": "No test claim without a test protocol and a result.",
        "care": "Care instructions for the label and PDP.",
        "hsn": "Candidate headings 6401-6405; confirm material and classification.",
        "legal_metrology": "MRP, country of origin, manufacturer, net quantity and consumer care.",
        "launch_date": "Drop 01 date is not set.",
        "discount_flip_note": "A discount can flip the GST rate; confirm the treatment with the CA.",
        "variants.foot_length_cm_status": "cm values are nominal; confirm against the last.",
        "image_convention.credit": "Photographer credit is not set.",
        "image_convention.release": "Model and location releases are not recorded.",
    }
    blocking = {
        "manufacturer": "PDP / launch",
        "CA": "tax / pricing",
        "last": "size guide",
        "founder": "launch / policy",
        "legal": "policy / label",
        "3PL": "cost model",
        "photography": "assets",
        "ops": "cost model",
        "attorney": "name clearance",
    }
    rows: list[dict[str, str]] = []

    def add(scope: str, product_id: str, field: str, value: str, note: str = "") -> None:
        owner = owner_of(value)
        rows.append(
            {
                "scope": scope,
                "product_id": product_id,
                "field": field,
                "current_value": value,
                "owner": owner,
                "blocking": blocking.get(owner, "review"),
                "notes": note or field_notes.get(field, ""),
            }
        )

    for product in products:
        for field, value in product.items():
            if isinstance(value, str) and "[TO CONFIRM" in value:
                add("product", product["product_id"], field, value)
        for variant in product["variants"]:
            value = variant["foot_length_cm_status"]
            if "[TO CONFIRM" in value:
                add("variant", product["product_id"], "variants.foot_length_cm_status", value, f"{variant['sku']}: {field_notes['variants.foot_length_cm_status']}")

    manual = [
        ("catalogue", "gst_rule.threshold_basis", TO_CONFIRM_CA, "Confirm whether the ₹2,500 threshold is measured before or after tax."),
        ("catalogue", "gst_rule.discount_flip", TO_CONFIRM_CA, "Confirm the GST rate when a discount moves the invoice across ₹2,500."),
        ("catalogue", "gst_rule.headings", TO_CONFIRM_CA, "Confirm the HSN heading for each product after materials are known."),
        ("catalogue", "target_landed_cost_inr", TO_CONFIRM_MFR, "All 30 target landed costs are planning assumptions; get supplier quotes."),
        ("size_guide", "size_system.half_sizes", TO_CONFIRM_MFR, "Half sizes are not in v1; confirm whether they are available."),
        ("size_guide", "size_system.width", TO_CONFIRM_MFR, "Do not claim wide fit until the last is measured."),
        ("size_guide", "size_system.cm_status", TO_CONFIRM_LAST, "Every cm value must be checked against the last."),
        ("image_convention", "image_convention.credit", TO_CONFIRM_PHOTO, "Photographer credit is not set."),
        ("image_convention", "image_convention.release", TO_CONFIRM_LEGAL, "Model and location releases are not recorded."),
        ("policy", "exchange_window", TO_CONFIRM_FOUNDER, "The 30-day window is confirmed for returns, not exchanges."),
        ("policy", "exchange_limit_basis", TO_CONFIRM_FOUNDER, "Confirm whether 'twice' is per order or per customer."),
        ("policy", "return_shipping", TO_CONFIRM_FOUNDER, "The founder has not said who pays return shipping."),
        ("policy", "fair_use_conditions", TO_CONFIRM_LEGAL, "Conditions for worn or damaged pairs need legal review."),
        ("policy", "post_30_day_defects", TO_CONFIRM_LEGAL, "No warranty in v1; confirm the post-30-day defect route."),
        ("cost_model", "reverse_logistics_per_exchange", TO_CONFIRM_3PL, "₹300 per exchange is a planning assumption; get a 3PL quote."),
        ("cost_model", "resale_recovery", TO_CONFIRM_OPS, "No resale recovery is assumed for returned pairs."),
        ("merchandising", "launch_date", TO_CONFIRM_FOUNDER, "Drop 01 date is not set."),
        ("merchandising", "size_curve", TO_CONFIRM_FOUNDER, "Do not set a size curve before fit-trial or pre-order data."),
        ("merchandising", "founder_story_facts", TO_CONFIRM_FOUNDER, "Founder-supplied story facts are still required before public use."),
        ("legal", "name_clearance", TO_CONFIRM_ATTORNEY, "Sāntvana is not cleared; no print, domain or ad spend."),
    ]
    for scope, field, value, note in manual:
        add(scope, "", field, value, note)

    rows.sort(key=lambda row: (row["scope"], row["product_id"], row["field"]))
    columns = ["scope", "product_id", "field", "current_value", "owner", "blocking", "notes"]
    write_csv(ROOT / "fields-to-confirm.csv", columns, rows)

    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        group = grouped.setdefault(
            row["field"],
            {
                "field": row["field"],
                "rows": 0,
                "owner": row["owner"],
                "blocking": row["blocking"],
                "notes": row["notes"],
            },
        )
        group["rows"] += 1
    summary_rows = sorted(grouped.values(), key=lambda item: (-item["rows"], item["field"]))

    lines = [
        "# Fields to confirm - Sāntvana Phase 3",
        "",
        "**Phase 3 · 31 October 2026 · concept only**",
        "Every `[TO CONFIRM]` in the catalogue data is listed here. The per-product, per-SKU list is `fields-to-confirm.csv`; this page is the summary.",
        "",
        "## How to use",
        "",
        "1. Send the manufacturer rows to the factory with the sample request. Do not publish a PDP until the construction, material, weight, sole, fit, care and origin rows are answered.",
        "2. Send the CA rows to the chartered accountant before setting the final price ladder or running a discount.",
        "3. Send the legal rows to the policy/label reviewer. The name-clearance row is already a Phase 1 blocker.",
        "4. Send the 3PL rows to the reverse-logistics partner before signing the exchange promise into the checkout.",
        "",
        "## Summary by field",
        "",
        "| Field | Rows | Owner | Blocking | Notes |",
        "|---|---:|---|---|---|",
    ]
    for item in summary_rows:
        lines.append(
            f"| `{item['field']}` | {item['rows']} | {item['owner']} | {item['blocking']} | {item['notes']} |"
        )
    lines += [
        "",
        "## What must clear before launch",
        "",
        "- **Manufacturer:** every material, weight, lug depth, sole compound, fit statement, care instruction and country of origin. The 268 g and 4 mm lugs in the Phase 1 sample copy are placeholders and are not in this catalogue.",
        "- **CA:** HSN classification, whether the ₹2,500 threshold is measured before or after tax, and the rate after a discount. The price ladder avoids the ambiguous zone, but discounts can enter it.",
        "- **Legal:** legal metrology, fair-use conditions, post-30-day defect route, image releases and the name-clearance opinion.",
        "- **3PL:** the ₹300 per-exchange reverse-logistics assumption and whether returned pairs can be resold.",
        "- **Founder:** exchange window, whether “twice” is per order or per customer, return shipping, Drop 01 date, size curve and founder story facts.",
        "",
        "## Full list",
        "",
        "`fields-to-confirm.csv` has one row per product field and one row per SKU cm value, plus the catalogue, size-guide, policy, cost-model, merchandising and legal rows.",
        "",
    ]
    (ROOT / "fields-to-confirm.md").write_text("\n".join(lines), encoding="utf-8")


def assert_internal_consistency(payload: dict[str, Any]) -> None:
    products = payload["products"]
    assert len(products) == 30, len(products)
    assert payload["catalogue"]["skus"] == 330
    assert payload["catalogue"]["gst_buckets"] == {"at_or_below_2500": 15, "above_2500": 15}
    assert payload["catalogue"]["tiers"] == {"good": 15, "better": 10, "best": 5}
    for category in CATEGORY_ORDER:
        category_products = [p for p in products if p["category"] == category]
        assert len(category_products) == 6, (category, len(category_products))
        assert sum(1 for p in category_products if p["tier"] == "good") == 3
        assert sum(1 for p in category_products if p["tier"] == "better") == 2
        assert sum(1 for p in category_products if p["tier"] == "best") == 1
    for product in products:
        assert product["gst_rate"] == (0.05 if product["price_inr"] <= 2500 else 0.18)
        assert len(product["variants"]) == 11
        assert len(product["images"]) == 4
        assert all(image["aspect"] == "4:5" for image in product["images"])
        assert all("[TO CONFIRM: manufacturer]" in product[field] for field in ["upper_material", "weight_g", "lug_depth_mm", "fit_note"])
    skus = [variant["sku"] for product in products for variant in product["variants"]]
    assert len(skus) == len(set(skus)) == 330


def main() -> None:
    payload = rupeeize(build_payload())
    assert_internal_consistency(payload)
    (ROOT / "products.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_products_csv(payload["products"])
    write_skus_csv(payload["products"])
    write_size_guide_csv()
    write_size_guide_md()
    write_pricing_table(payload["products"])
    write_fields_to_confirm(payload["products"])

    avg_net = sum(Decimal(str(p["net_revenue_inr"])) for p in payload["products"]) / len(payload["products"])
    avg_gm = sum(Decimal(str(p["gross_margin_inr"])) for p in payload["products"]) / len(payload["products"])
    avg_margin = avg_gm / avg_net * Decimal("100")
    print("Wrote 30 products and 330 SKUs.")
    print("GST buckets: 15 at/below Rs 2,500 (5%), 15 above (18%).")
    print(f"Average net revenue: Rs {money_text(avg_net)}; average gross margin: Rs {money_text(avg_gm)} ({pct_text(avg_margin)}).")
    print("Files: products.json, products.csv, skus.csv, size-guide.csv, size-guide.md,")
    print("       pricing-table.md, fields-to-confirm.csv, fields-to-confirm.md")


if __name__ == "__main__":
    main()
