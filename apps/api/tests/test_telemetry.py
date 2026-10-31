from __future__ import annotations

from app import telemetry


def test_telemetry_is_disabled_by_default() -> None:
    telemetry._configured = False
    telemetry.configure_telemetry(None)
    assert telemetry.telemetry_configured() is False
