"""Contact masking for the public order endpoint.

The order URL is a capability token until authentication ships. Masking keeps
the confirmation page useful without putting a full email address or mobile
number in browser history, logs, screenshots or shared links.
"""

from __future__ import annotations

import re


def mask_email(value: str | None) -> str:
    if not value or "@" not in value:
        return "***"
    local, domain = value.split("@", 1)
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def mask_phone(value: str | None) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) < 4:
        return "***"
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"
