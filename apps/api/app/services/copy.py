"""Customer-facing copy rules.

The Phase 3 catalogue was written for internal planning and contains ladder
language ("best-tier", "better-tier", "halo of the range") plus return and
exchange promises that are still waiting on the founder. None of that may reach
a customer. This module rewrites the text at seed time and is also used by the
tests as the definition of the banned terms.
"""

from __future__ import annotations

import re

TIER_RE = re.compile(r"\b(?:the|a|an)\s+(?:best|better|good)[- ]tier\s+", re.IGNORECASE)
TIER_ANY_RE = re.compile(r"\b(?:best|better|good)[- ]tier\b", re.IGNORECASE)
HALO_RE = re.compile(
    r"\bthe halo of the (?:[a-z]+ )?range\s*[;,]?\s*", re.IGNORECASE
)
UNCONFIRMED_CLAIM_RE = re.compile(
    r"(free size exchange|size exchange twice|exchange twice|30-day returns|"
    r"returns from delivery|free returns|return shipping)",
    re.IGNORECASE,
)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
SPACE_RE = re.compile(r"\s+")

BANNED_CUSTOMER_TERMS = (
    "best-tier",
    "better-tier",
    "good-tier",
    "halo of the range",
    "free size exchange",
    "size exchange twice",
    "exchange twice",
    "30-day returns",
    "returns from delivery",
    "free returns",
    "return shipping",
)


def _capitalise(sentence: str) -> str:
    stripped = sentence.strip()
    if not stripped:
        return ""
    return stripped[0].upper() + stripped[1:]


def sanitise_customer_text(value: str | None) -> str | None:
    """Remove ladder language and unconfirmed service promises from copy."""

    if not value:
        return value
    text = TIER_RE.sub("A ", value)
    text = TIER_ANY_RE.sub("", text)
    text = HALO_RE.sub("", text)
    sentences = []
    for sentence in SENTENCE_SPLIT_RE.split(text):
        if UNCONFIRMED_CLAIM_RE.search(sentence):
            continue
        cleaned = _capitalise(sentence)
        if cleaned:
            sentences.append(cleaned)
    result = SPACE_RE.sub(" ", " ".join(sentences)).strip()
    result = re.sub(r"\bA a\b", "A", result)
    result = re.sub(r"\s+([.;,])", r"\1", result)
    return result or None


def sanitise_features(values: object) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        if contains_banned_copy(value):
            continue
        result.append(value.strip())
    return result


def contains_banned_copy(value: object) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(term in lowered for term in BANNED_CUSTOMER_TERMS)
    if isinstance(value, (list, tuple)):
        return any(contains_banned_copy(item) for item in value)
    return False
