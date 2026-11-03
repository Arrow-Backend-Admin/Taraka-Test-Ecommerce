"""Money and GST helpers.

Every amount that leaves the API is an integer number of paise. Floating point
never touches a price. The catalogue stores GST-inclusive MRP, so the GST inside
a line is extracted from the line total rather than added on top.

The GST rate is taken from the product snapshot when present. Otherwise it is
derived from the unit sale value: footwear at or below ₹2,500 is 5%, above it is
18%. Discounts are not applied in this milestone, so the unit sale value is the
catalogue price. The threshold basis and the discount-crossing treatment are
still with the CA; see brand/phase-3/fields-to-confirm.md.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

GST_REDUCED_PCT = 5
GST_STANDARD_PCT = 18
GST_THRESHOLD_PAISE = 250_000  # ₹2,500


def rupees_to_paise(value: Any) -> int:
    if value is None:
        return 0
    amount = value if isinstance(value, Decimal) else Decimal(str(value))
    return int(
        (amount * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def paise_to_rupees(value: int) -> Decimal:
    return (Decimal(value) / Decimal(100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def gst_rate_pct(unit_price_paise: int, catalogue_rate: Any = None) -> int:
    """Return 5 or 18 for one pair.

    ``catalogue_rate`` is the Phase 3 rate stored as a decimal fraction
    (0.05 / 0.18). If it is missing or unexpected, fall back to the threshold.
    """

    if catalogue_rate is not None:
        try:
            rate = int((Decimal(str(catalogue_rate)) * 100).quantize(Decimal("1")))
        except Exception:  # noqa: BLE001 - bad catalogue data falls back to the rule
            rate = 0
        if rate in (GST_REDUCED_PCT, GST_STANDARD_PCT):
            return rate
    return GST_REDUCED_PCT if unit_price_paise <= GST_THRESHOLD_PAISE else GST_STANDARD_PCT


def split_gst(line_total_paise: int, rate_pct: int) -> tuple[int, int]:
    """Split GST out of a GST-inclusive line total.

    Returns ``(taxable_value_paise, gst_paise)``. The two always add back to the
    line total, so the customer is never charged a rounding difference.
    """

    if line_total_paise < 0:
        raise ValueError("line_total_paise must not be negative")
    rate = Decimal(rate_pct)
    gst = (
        Decimal(line_total_paise) * rate / (Decimal(100) + rate)
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    gst_paise = int(gst)
    return line_total_paise - gst_paise, gst_paise
