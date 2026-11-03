from __future__ import annotations

import json
from pathlib import Path

from app.services.copy import (
    BANNED_CUSTOMER_TERMS,
    contains_banned_copy,
    sanitise_customer_text,
    sanitise_features,
)

CATALOGUE = (
    Path(__file__).resolve().parents[3] / "brand" / "phase-3" / "products.json"
)

CLEAN_SENTENCES = (
    "A low-top sneaker in slate.",
    "A more considered silhouette for the launch range.",
    "Sizes UK 3 to 13.",
    "The final last is pending manufacturer confirmation.",
    "Designed for the walk between transport and desk.",
    "A boot in moss with a clean, grounded line.",
)


def test_clean_sentences_are_never_altered() -> None:
    """copy.py is a safety net, not a copy editor.

    A sentence that contains none of the banned phrases must pass through
    byte-for-byte. This is the guard that stops the sanitiser silently
    rewriting customer copy at seed time.
    """

    for sentence in CLEAN_SENTENCES:
        assert not contains_banned_copy(sentence)
        assert sanitise_customer_text(sentence) == sentence


def test_generated_catalogue_descriptions_need_no_sanitising() -> None:
    """Descriptions are fixed at source in brand/phase-3/build_catalogue.py."""

    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    for product in payload["products"]:
        for field in ("short_description", "long_description"):
            text = product[field]
            assert not contains_banned_copy(text), (product["slug"], field, text)
            assert sanitise_customer_text(text) == text, (product["slug"], field)


def test_ladder_language_is_removed() -> None:
    text = (
        "The best-tier everyday shoe. A better-tier option for the commute. "
        "This is the halo of the range; a quiet profile."
    )
    cleaned = sanitise_customer_text(text)

    assert cleaned is not None
    assert not contains_banned_copy(cleaned)
    for term in ("best-tier", "better-tier", "halo of the range"):
        assert term not in cleaned.lower()
    assert "quiet profile" in cleaned


def test_unconfirmed_service_promises_are_dropped() -> None:
    text = (
        "A clean court silhouette. Free size exchange within 30 days. "
        "30-day returns from delivery. Made for daily wear."
    )
    cleaned = sanitise_customer_text(text)

    assert cleaned is not None
    assert "Free size exchange" not in cleaned
    assert "30-day returns" not in cleaned
    assert "clean court silhouette" in cleaned.lower()
    assert "daily wear" in cleaned


def test_features_drop_banned_claims_and_keep_safe_lines() -> None:
    features = [
        "Cushioned footbed",
        "Free returns",
        "the halo of the range",
        "Flexible outsole",
    ]
    assert sanitise_features(features) == ["Cushioned footbed", "Flexible outsole"]


def test_banned_terms_cover_the_known_internal_language() -> None:
    for term in ("best-tier", "better-tier", "halo of the range", "free returns"):
        assert term in BANNED_CUSTOMER_TERMS
        assert contains_banned_copy(f"copy with {term} inside")
