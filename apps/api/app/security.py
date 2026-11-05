"""HTTP hardening middleware and log redaction.

The API is JSON only. These helpers add the deployment-wide guards that do not
belong to one route: a hard request-body limit, security headers, a strict
Content-Security-Policy for API responses, and a logging filter that removes
contact details and credentials from log lines.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

Message = MutableMapping[str, Any]
Scope = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class BodyTooLarge(Exception):
    pass


class RequestSizeLimitMiddleware:
    """Reject bodies above ``max_bytes`` before the application reads them.

    The body is buffered once (the API is JSON, not a streaming upload) and
    replayed to the app. A missing or lying Content-Length is still bounded by
    the actual byte count.
    """

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        declared = 0
        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    declared = int(value)
                except ValueError:
                    declared = 0
                break
        if declared > self.max_bytes:
            await _send_json(send, 413, {"detail": "Request body is too large"})
            return

        chunks: list[bytes] = []
        total = 0
        more = True
        while more:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            total += len(chunk)
            if total > self.max_bytes:
                await _send_json(
                    send, 413, {"detail": "Request body is too large"}
                )
                return
            chunks.append(chunk)
            more = bool(message.get("more_body", False))
        body = b"".join(chunks)
        replayed = False

        async def replay() -> Message:
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        await self.app(scope, replay, send)


class SecurityHeadersMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        production: bool = False,
        csp: str | None = None,
    ) -> None:
        self.app = app
        self.production = production
        self.csp = csp or (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; "
            "form-action 'none'"
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"no-referrer"),
                        (b"permissions-policy", b"interest-cohort=()"),
                        (b"content-security-policy", self.csp.encode("latin-1")),
                    ]
                )
                if self.production:
                    headers.append(
                        (
                            b"strict-transport-security",
                            b"max-age=31536000; includeSubDomains",
                        )
                    )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


async def _send_json(send: Send, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body, "more_body": False})


EMAIL_RE = re.compile(
    r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[- ]?)?([6-9]\d{4})[- ]?(\d{5})(?!\d)")
BEARER_RE = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+")
SECRET_RE = re.compile(
    r"(?i)((?:secret|token|password|api[_-]?key|authorization)\s*[:=]\s*)[^\s,;]+"
)
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def _mask_phone(match: re.Match[str]) -> str:
    return f"******{match.group(2)}"


def redact(value: str) -> str:
    """Remove PII and credentials from one log message."""

    value = EMAIL_RE.sub(r"\1***\2", value)
    value = PHONE_RE.sub(_mask_phone, value)
    value = BEARER_RE.sub(r"\1[REDACTED]", value)
    value = SECRET_RE.sub(r"\1[REDACTED]", value)
    value = CARD_RE.sub("[REDACTED-CARD]", value)
    return value


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - never break logging
            return True
        record.msg = redact(message)
        record.args = ()
        return True


class RedactingFormatter(logging.Formatter):
    """Redact the fully formatted record, including any traceback text."""

    def __init__(self, inner: logging.Formatter | None = None) -> None:
        super().__init__()
        self._inner = inner or logging.Formatter()

    def format(self, record: logging.LogRecord) -> str:
        return redact(self._inner.format(record))


def _install_on(logger: logging.Logger) -> None:
    if not any(isinstance(item, RedactingFilter) for item in logger.filters):
        logger.addFilter(RedactingFilter())
    for handler in logger.handlers:
        if not isinstance(handler.formatter, RedactingFormatter):
            handler.setFormatter(RedactingFormatter(handler.formatter))


def install_log_redaction() -> None:
    # The root logger covers application logs. Uvicorn configures its own
    # access/error loggers with propagate disabled, so cover them explicitly:
    # access lines contain query strings, which may carry contact details.
    for name in ("", "uvicorn", "uvicorn.access", "uvicorn.error"):
        _install_on(logging.getLogger(name))
