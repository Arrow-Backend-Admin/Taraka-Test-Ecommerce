from __future__ import annotations

import logging
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from .config import get_settings
from .db import engine

logger = logging.getLogger(__name__)

_configured = False


def telemetry_configured() -> bool:
    return _configured


def _headers(raw: str | None) -> dict[str, str] | None:
    if not raw:
        return None
    headers: dict[str, str] = {}
    for pair in raw.split(","):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        headers[key.strip()] = value.strip()
    return headers or None


def configure_telemetry(app: Any | None) -> None:
    """Instrument FastAPI and SQLAlchemy once.

    Disabled by default so local tests do not export spans. Set OTEL_ENABLED=true
    and OTEL_EXPORTER_OTLP_ENDPOINT to send traces to a collector. Without an
    endpoint, spans go to the console for local inspection.
    """

    global _configured
    if _configured:
        return

    settings = get_settings()
    if not settings.otel_enabled:
        return

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": "0.1.0",
            "deployment.environment": settings.environment,
        }
    )
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            headers=_headers(settings.otel_exporter_otlp_headers),
        )
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    SQLAlchemyInstrumentor().instrument(engine=engine, tracer_provider=provider)

    _configured = True
    logger.info("OpenTelemetry enabled for %s", settings.otel_service_name)
