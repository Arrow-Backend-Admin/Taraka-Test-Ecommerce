#!/usr/bin/env python3
"""Validate the Sāntvana Phase 3 catalogue without a database.

Run from the repository root:
    python brand/phase-3/validate_catalogue.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TWO_PLACES = Decimal("0.01")
CONFIRM_RE = re.compile(r"\[TO CONFIRM:\s*([^\]]+)\]")
IMAGE_RE = re.compile(r"^drop-01_[a-z0-9-]+_(hero-45|side-profile|sole-macro|on-foot-34)_4x5_v01\.jpg$")
SKU_RE = re.compile(r"^[A-Z]{2}-[A-Z]{2,4}-[A-Z]{3}-UK(?:[3-9]|1[0-3])$")

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def q(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def money(value: Decimal | int | str) -> float:
    return float(q(value))


def pct(value: Decimal | int | str) -> float:
    return float(q(value))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(walk_strings(item))
        return result
    if isinstance(value, dict):
        result = []
        for item in value.values():
            result.extend(walk_strings(item))
        return result
    return []


def main() -> int:
    products_path = ROOT / "products.json"
    check(products_path.exists(), "products.json is missing")
    if not products_path.exists():
        print("FAIL: products.json is missing")
        return 1

    payload = json.loads(products_path.read_text(encoding="utf-8"))
    products = payload.get("products", [])

    # Top-level shape
    check(payload.get("schema_version") == "1.0.0", "schema_version must be 1.0.0")
    check(payload.get("generated_at") == "2026-10-31", "generated_at must be 2026-10-31")
    check(payload.get("brand") == "Sāntvana", "brand must be Sāntvana")
    check("concept" in payload.get("status", ""), "status must be concept")
    check(payload.get("currency") == "INR", "currency must be INR")
    check(payload.get("market") == "India only", "market must be India only")
    check(payload.get("price_band_inr") == [2299, 4999], "price_band_inr must be [2299, 4999]")
    check(payload.get("core_price_band_inr") == [2299, 4999], "core_price_band_inr must be [2299, 4999]")

    catalogue = payload.get("catalogue", {})
    check(catalogue.get("products") == 30, "catalogue.products must be 30")
    check(catalogue.get("categories") == 5, "catalogue.categories must be 5")
    check(catalogue.get("products_per_category") == 6, "products_per_category must be 6")
    check(catalogue.get("tiers") == {"good": 15, "better": 10, "best": 5}, "tier counts must be 15/10/5")
    check(
        catalogue.get("gst_buckets") == {"at_or_below_2500": 15, "above_2500": 15},
        "GST bucket counts must be 15/15",
    )
    check(catalogue.get("skus") == 330, "catalogue.skus must be 330")
    check(catalogue.get("sizes_per_product") == 11, "sizes_per_product must be 11")

    gst_rule = payload.get("gst_rule", {})
    check(gst_rule.get("threshold_inr_per_pair") == 2500, "GST threshold must be ₹2,500")
    check(gst_rule.get("rates") == {"at_or_below_2500": 0.05, "above_2500": 0.18}, "GST rates must be 5%/18%")
    check(gst_rule.get("basis") == "invoice sale value, whole pair", "GST basis must be invoice sale value, whole pair")
    check("[TO CONFIRM: CA]" in str(gst_rule.get("threshold_basis", "")), "GST threshold basis must be [TO CONFIRM: CA]")
    check("chartered accountant" in str(gst_rule.get("ca_confirmation", "")).lower(), "CA confirmation sentence is missing")
    check("discount" in str(gst_rule.get("discount_flip", "")).lower(), "discount flip note is missing")

    size_system = payload.get("size_system", {})
    check(size_system.get("uk_range") == "UK 3-13", "size range must be UK 3-13")
    check(size_system.get("whole_sizes_only") is True, "whole_sizes_only must be true")
    check("[TO CONFIRM: manufacturer]" in str(size_system.get("half_sizes", "")), "half sizes must be flagged")
    check("[TO CONFIRM: manufacturer]" in str(size_system.get("width", "")), "width must be flagged")
    check("[TO CONFIRM: last]" in str(size_system.get("cm_status", "")), "cm status must be flagged")
    check(len(size_system.get("rows", [])) == 11, "size_system.rows must have 11 rows")

    image_convention = payload.get("image_convention", {})
    check(image_convention.get("aspect") == "4:5", "image aspect must be 4:5")
    check(image_convention.get("pattern") == "drop-01_<product-slug>_<role>_4x5_v01.jpg", "image pattern is wrong")
    check(image_convention.get("roles") == ["hero-45", "side-profile", "sole-macro", "on-foot-34"], "image roles are wrong")
    check("[TO CONFIRM: photography]" in str(image_convention.get("credit", "")), "image credit must be flagged")
    check("[TO CONFIRM: legal]" in str(image_convention.get("release", "")), "image release must be flagged")

    claims = payload.get("claims_register", {})
    check("Free size exchange twice" in claims.get("confirmed", []), "confirmed exchange claim is missing")
    check("30-day returns from delivery" in claims.get("confirmed", []), "confirmed returns claim is missing")
    check("slip-proof" in claims.get("banned_in_v1", []), "banned slip-proof claim is missing")
    check("vegan" in claims.get("banned_in_v1", []), "banned vegan claim is missing")

    placeholders = " ".join(payload.get("placeholders_not_used", []))
    check("268 g" in placeholders, "268 g placeholder note is missing")
    check("4 mm lugs" in placeholders, "4 mm lugs placeholder note is missing")

    # Products
    check(len(products) == 30, f"expected 30 products, found {len(products)}")
    category_counts = Counter(product.get("category") for product in products)
    for category in ["Sneakers", "Running", "Everyday", "Sandals", "Boots"]:
        check(category_counts.get(category) == 6, f"{category} must have 6 products")

    tier_counts = Counter(product.get("tier") for product in products)
    check(tier_counts.get("good") == 15, "good tier must have 15 products")
    check(tier_counts.get("better") == 10, "better tier must have 10 products")
    check(tier_counts.get("best") == 5, "best tier must have 5 products")

    product_ids: list[str] = []
    slugs: list[str] = []
    sku_list: list[str] = []
    heroes: list[dict[str, Any]] = []
    for product in products:
        pid = product.get("product_id", "")
        product_ids.append(pid)
        slugs.append(product.get("slug", ""))
        name = product.get("name", "")
        price = product.get("price_inr")
        rate = product.get("gst_rate")
        check(isinstance(price, int), f"{pid}: price_inr must be an integer")
        check(rate in (0.05, 0.18), f"{pid}: gst_rate must be 0.05 or 0.18")
        check(rate == (0.05 if price <= 2500 else 0.18), f"{pid}: gst_rate does not match price")
        check(product.get("gst_bucket") == ("at_or_below_2500" if price <= 2500 else "above_2500"), f"{pid}: gst_bucket is wrong")
        check(not (2500 < price < 3499), f"{pid}: price {price} sits in the avoided ₹2,501-₹3,498 zone")
        net = money(Decimal(price) / (Decimal("1") + Decimal(str(rate))))
        gm = money(Decimal(str(net)) - Decimal(str(product.get("target_landed_cost_inr"))))
        gmp = pct(Decimal(str(gm)) / Decimal(str(net)) * Decimal("100"))
        check(product.get("net_revenue_inr") == net, f"{pid}: net_revenue_inr is {product.get('net_revenue_inr')}, expected {net}")
        check(product.get("gross_margin_inr") == gm, f"{pid}: gross_margin_inr is {product.get('gross_margin_inr')}, expected {gm}")
        check(product.get("gross_margin_pct") == gmp, f"{pid}: gross_margin_pct is {product.get('gross_margin_pct')}, expected {gmp}")
        check(product.get("gst_amount_inr") == money(Decimal(price) - Decimal(str(net))), f"{pid}: gst_amount_inr is wrong")
        low = product.get("margin_target_low_pct")
        high = product.get("margin_target_high_pct")
        check(low <= gmp <= high, f"{pid}: margin {gmp}% outside target {low}-{high}%")
        if price > 2500:
            expected_threshold = pct((Decimal("1") - Decimal("2500") / Decimal(price)) * Decimal("100"))
            check(
                product.get("discount_flip_threshold_pct") == expected_threshold,
                f"{pid}: discount flip threshold is wrong",
            )
        else:
            check(product.get("discount_flip_threshold_pct") is None, f"{pid}: discount threshold must be null at or below ₹2,500")
        check(product.get("price_basis") == "GST-inclusive MRP", f"{pid}: price basis must be GST-inclusive MRP")
        check(product.get("status") == "concept", f"{pid}: status must be concept")
        check("not trademark cleared" in str(product.get("name_status", "")), f"{pid}: name status must flag clearance")
        check(product.get("size_run") == "UK 3-13", f"{pid}: size run must be UK 3-13")
        check(product.get("sku_count") == 11, f"{pid}: sku_count must be 11")
        check(product.get("hero") is True or product.get("hero") is False, f"{pid}: hero must be boolean")
        if product.get("hero"):
            heroes.append(product)

        # Product facts must be unconfirmed, not invented.
        for field in [
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
        ]:
            check("[TO CONFIRM: manufacturer]" in str(product.get(field, "")), f"{pid}: {field} must be [TO CONFIRM: manufacturer]")
        check("[TO CONFIRM: CA]" in str(product.get("hsn", "")), f"{pid}: hsn must be [TO CONFIRM: CA]")
        check("[TO CONFIRM: legal]" in str(product.get("legal_metrology", "")), f"{pid}: legal_metrology must be [TO CONFIRM: legal]")
        check("[TO CONFIRM: founder]" in str(product.get("launch_date", "")), f"{pid}: launch_date must be [TO CONFIRM: founder]")
        check(product.get("performance_claims") == [], f"{pid}: performance_claims must be empty")
        check(len(product.get("claims", [])) == 2, f"{pid}: exactly two confirmed policy claims are expected")
        check(all(claim.get("status") == "confirmed policy" for claim in product.get("claims", [])), f"{pid}: claims must be confirmed policy only")

        # Variants
        variants = product.get("variants", [])
        check(len(variants) == 11, f"{pid}: expected 11 variants, found {len(variants)}")
        expected_sizes = {f"UK {size}" for size in range(3, 14)}
        check({variant.get("size_uk") for variant in variants} == expected_sizes, f"{pid}: size labels must be UK 3-13")
        for variant in variants:
            sku = variant.get("sku", "")
            sku_list.append(sku)
            check(SKU_RE.match(sku) is not None, f"{pid}: bad SKU pattern: {sku}")
            check(variant.get("size_uk", "").replace("UK ", "") in {str(size) for size in range(3, 14)}, f"{pid}: bad UK size")
            check("[TO CONFIRM: last]" in str(variant.get("foot_length_cm_status", "")), f"{pid}: cm status must be flagged")
            check(variant.get("price_inr") == price, f"{pid}: variant price mismatch")
            check(variant.get("gst_rate") == rate, f"{pid}: variant GST mismatch")
            check(variant.get("net_revenue_inr") == net, f"{pid}: variant net revenue mismatch")
            check(variant.get("stock_status") == "not_allocated", f"{pid}: stock status must be not_allocated")

        # Images
        images = product.get("images", [])
        check(len(images) == 4, f"{pid}: expected 4 images, found {len(images)}")
        check({image.get("role") for image in images} == {"hero-45", "side-profile", "sole-macro", "on-foot-34"}, f"{pid}: image roles are wrong")
        for image in images:
            filename = image.get("filename", "")
            check(IMAGE_RE.match(filename) is not None, f"{pid}: bad image filename: {filename}")
            check(image.get("aspect") == "4:5", f"{pid}: image aspect must be 4:5")
            check(image.get("status") == "brief only; no asset", f"{pid}: image status must be brief only")
            check("Sāntvana" not in image.get("alt", ""), f"{pid}: alt text should not stuff the brand name")

        # No placeholder numbers in product copy.
        for text in walk_strings(product):
            check("268 g" not in text, f"{pid}: 268 g placeholder leaked into product data")
            check("4 mm lugs" not in text, f"{pid}: 4 mm lugs placeholder leaked into product data")
            for banned in ["slip-proof", "tested on wet tile", "fits Indian feet", "grip that grips wet tile", "vegan", "recycled", "sustainable"]:
                check(banned not in text.lower(), f"{pid}: banned claim '{banned}' leaked into product data")

    check(len(product_ids) == len(set(product_ids)), "product_id values must be unique")
    check(len(slugs) == len(set(slugs)), "slugs must be unique")
    check(len(sku_list) == len(set(sku_list)) == 330, "SKUs must be unique and total 330")
    check(len(heroes) == 5, "there must be 5 hero products")
    check({hero.get("category") for hero in heroes} == {"Sneakers", "Running", "Everyday", "Sandals", "Boots"}, "heroes must cover all 5 categories")

    # CSV checks
    products_csv = read_csv(ROOT / "products.csv")
    skus_csv = read_csv(ROOT / "skus.csv")
    size_guide_csv = read_csv(ROOT / "size-guide.csv")
    check(len(products_csv) == 30, f"products.csv must have 30 rows, found {len(products_csv)}")
    check(len(skus_csv) == 330, f"skus.csv must have 330 rows, found {len(skus_csv)}")
    check(len(size_guide_csv) == 11, f"size-guide.csv must have 11 rows, found {len(size_guide_csv)}")
    check({row.get("product_id") for row in products_csv} == set(product_ids), "products.csv product IDs do not match JSON")
    check({row.get("sku") for row in skus_csv} == set(sku_list), "skus.csv SKUs do not match JSON")

    # Fields-to-confirm coverage
    fields_csv = read_csv(ROOT / "fields-to-confirm.csv")
    actual_fields = {(row.get("product_id", ""), row.get("field", "")) for row in fields_csv}
    expected_fields: set[tuple[str, str]] = set()
    for product in products:
        pid = product.get("product_id", "")
        for field, value in product.items():
            if isinstance(value, str) and "[TO CONFIRM" in value:
                expected_fields.add((pid, field))
        expected_fields.add((pid, "variants.foot_length_cm_status"))
    check(expected_fields.issubset(actual_fields), "fields-to-confirm.csv is missing product or variant fields")
    check(len(fields_csv) >= 1000, "fields-to-confirm.csv looks too small")
    manual_fields = {
        "gst_rule.threshold_basis",
        "gst_rule.discount_flip",
        "gst_rule.headings",
        "target_landed_cost_inr",
        "size_system.half_sizes",
        "size_system.width",
        "size_system.cm_status",
        "image_convention.credit",
        "image_convention.release",
        "exchange_window",
        "exchange_limit_basis",
        "return_shipping",
        "fair_use_conditions",
        "post_30_day_defects",
        "reverse_logistics_per_exchange",
        "resale_recovery",
        "launch_date",
        "size_curve",
        "founder_story_facts",
        "name_clearance",
    }
    check(manual_fields.issubset({row.get("field", "") for row in fields_csv}), "fields-to-confirm.csv is missing manual rows")
    for row in fields_csv:
        match = CONFIRM_RE.search(row.get("current_value", ""))
        check(match is not None, f"fields-to-confirm.csv row has no [TO CONFIRM]: {row}")
        if match:
            check(row.get("owner") == match.group(1).strip(), f"fields-to-confirm.csv owner mismatch: {row}")

    # Generated document checks
    for filename in ["size-guide.md", "pricing-table.md", "fields-to-confirm.md"]:
        path = ROOT / filename
        check(path.exists(), f"{filename} is missing")
        if path.exists():
            text = path.read_text(encoding="utf-8")
            check("[TO CONFIRM" in text, f"{filename} must retain [TO CONFIRM] flags")
    if (ROOT / "pricing-table.md").exists():
        pricing_text = (ROOT / "pricing-table.md").read_text(encoding="utf-8")
        check(pricing_text.count("| Good |") == 15, "pricing-table.md must show 15 Good rows")
        check(pricing_text.count("| Better |") == 10, "pricing-table.md must show 10 Better rows")
        check(pricing_text.count("| Best |") == 5, "pricing-table.md must show 5 Best rows")

    # Summary
    avg_net = sum(Decimal(str(p["net_revenue_inr"])) for p in products) / len(products)
    avg_gm = sum(Decimal(str(p["gross_margin_inr"])) for p in products) / len(products)
    avg_margin = avg_gm / avg_net * Decimal("100")

    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for message in errors[:60]:
            print(f"- {message}")
        if len(errors) > 60:
            print(f"- ... and {len(errors) - 60} more")
        return 1

    print("PASS: catalogue validation")
    print("30 products, 5 categories x 6, 330 SKUs, 11 sizes per product.")
    print("15 products at/below ₹2,500 (5% GST); 15 above (18% GST).")
    print("5 heroes, one per category.")
    print(f"Average net revenue ₹{q(avg_net):,.2f}; average gross margin ₹{q(avg_gm):,.2f} ({q(avg_margin):.2f}%).")
    print("All product facts retain [TO CONFIRM] flags; 268 g and 4 mm lugs are not used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
