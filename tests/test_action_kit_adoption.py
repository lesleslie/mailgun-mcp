"""Tests for Oneiric action-kit adoption in mailgun-mcp.

Wave 3 (W3) migration:
- ``verify_webhook_signature`` -> oneiric.actions.security.SecuritySignatureAction
- ``notify_webhook_event`` -> oneiric.actions.workflow.WorkflowNotifyAction

The kit caches are module-level ``lru_cache`` singletons; tests clear them
via the public ``cache_clear()`` to avoid state pollution between cases.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import time

import pytest

from mailgun_mcp.main import (
    WEBHOOK_MAX_TIMESTAMP_SKEW_SECONDS,
    _webhook_notify_action,
    _webhook_signature_action,
    notify_webhook_event,
    verify_webhook_signature,
)


@pytest.fixture(autouse=True)
def _reset_action_kit_caches() -> None:
    """Reset module-level lru_caches so each test gets a fresh action."""
    _webhook_signature_action.cache_clear()
    _webhook_notify_action.cache_clear()
    yield
    _webhook_signature_action.cache_clear()
    _webhook_notify_action.cache_clear()


def _run(coro):
    return asyncio.run(coro)


def test_signature_action_is_singleton() -> None:
    """The cached signature action is the canonical HMAC-SHA256 envelope."""
    action = _webhook_signature_action()
    assert action._settings.algorithm == "sha256"
    assert action._settings.encoding == "hex"
    # header_name is left at the kit default (X-Oneiric-Signature); the
    # mailgun wrapper doesn't emit outbound headers so the setting is
    # never used for outbound signing.
    assert action._settings.header_name == "X-Oneiric-Signature"
    # Same instance returned across calls (lru_cache hit).
    assert _webhook_signature_action() is action


def test_notify_action_is_singleton() -> None:
    action = _webhook_notify_action()
    assert action._settings.default_channel == "mailgun-webhook"
    assert action._settings.require_message is True
    assert _webhook_notify_action() is action


def test_verify_webhook_signature_accepts_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """A signature computed with the API key over timestamp||token verifies."""
    api_key = "key-deadbeefcafebabe1234"
    timestamp = str(int(time.time()))
    token = "abcdef0123456789"
    expected = hmac.new(
        api_key.encode("utf-8"),
        f"{timestamp}{token}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: api_key)

    result = _run(verify_webhook_signature(timestamp, token, expected))

    assert result["verified"] is True
    assert result["algorithm"] == "sha256"
    assert result["encoding"] == "hex"


def test_verify_webhook_signature_rejects_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A wrong signature fails verification without leaking timing info."""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "real-key")

    result = _run(verify_webhook_signature(str(int(time.time())), "tok", "0" * 64))

    assert result["verified"] is False
    assert result["algorithm"] == "sha256"


def test_verify_webhook_signature_errors_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    result = _run(verify_webhook_signature(str(int(time.time())), "tok", "x"))

    assert result["verified"] is False
    assert "MAILGUN_API_KEY" in result["error"]


def test_verify_webhook_signature_rejects_stale_timestamp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Replay protection: signatures older than the skew window are rejected."""
    api_key = "k"
    old_ts = int(time.time()) - WEBHOOK_MAX_TIMESTAMP_SKEW_SECONDS - 60
    token = "tok"
    # Build a valid-looking signature; the check should reject before compare.
    valid_sig = hmac.new(
        api_key.encode(), f"{old_ts}{token}".encode(), hashlib.sha256
    ).hexdigest()

    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: api_key)
    result = _run(verify_webhook_signature(str(old_ts), token, valid_sig))

    assert result["verified"] is False
    assert result["error"] == "signature expired"


def test_verify_webhook_signature_rejects_future_timestamp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Far-future timestamps are also rejected (clock-skew / forgery)."""
    api_key = "k"
    future_ts = int(time.time()) + WEBHOOK_MAX_TIMESTAMP_SKEW_SECONDS + 60
    token = "tok"
    valid_sig = hmac.new(
        api_key.encode(), f"{future_ts}{token}".encode(), hashlib.sha256
    ).hexdigest()

    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: api_key)
    result = _run(verify_webhook_signature(str(future_ts), token, valid_sig))

    assert result["verified"] is False
    assert result["error"] == "signature expired"


def test_verify_webhook_signature_rejects_non_numeric_timestamp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_key = "k"
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: api_key)

    result = _run(verify_webhook_signature("not-a-number", "tok", "x"))

    assert result["verified"] is False
    assert result["error"] == "invalid timestamp"


def test_notify_webhook_event_returns_logged_envelope() -> None:
    result = _run(
        notify_webhook_event(
            message="webhook delivered",
            context={"message_id": "<abc@example.com>", "event": "delivered"},
        )
    )

    assert result["status"] == "logged"
    assert result["channel"] == "mailgun-webhook"
    assert result["level"] == "info"
    assert result["message"] == "webhook delivered"
    assert result["context"]["message_id"] == "<abc@example.com>"


def test_notify_webhook_event_uses_overrides() -> None:
    result = _run(
        notify_webhook_event(
            message="webhook failed",
            channel="alerts",
            level="error",
        )
    )

    assert result["status"] == "logged"
    assert result["channel"] == "alerts"
    assert result["level"] == "error"


def test_verify_signature_uses_oneiric_action_not_reimplemented_hmac(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sanity check: the call path actually routes through SecuritySignatureAction.

    If someone refactors the function to bypass the kit, this test fails —
    preserving the W3 invariant that the canonical signing envelope is the
    only one in play.
    """
    called = {"flag": False}
    original_execute = _webhook_signature_action().execute

    async def spy_execute(payload):
        called["flag"] = True
        return await original_execute(payload)

    class _Spy:
        execute = staticmethod(spy_execute)

    monkeypatch.setattr("mailgun_mcp.main._webhook_signature_action", lambda: _Spy())
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "key")

    _run(verify_webhook_signature(str(int(time.time())), "tok", "0" * 64))

    assert called["flag"] is True, (
        "verify_webhook_signature must route through SecuritySignatureAction"
    )
