"""
Schema validation tests for Pydantic models.

This test module provides schema validation tests for Pydantic models in the
mailgun-mcp project. As of now, the project does not use Pydantic models -
all API responses are plain dictionaries. This file serves as a template
and documentation for when Pydantic models are introduced.

When Pydantic models are added to this project, they should:
1. Use model_config with extra="ignore" or extra="allow" to handle
   unexpected fields from the Mailgun API
2. Be placed in a models/ directory under mailgun_mcp/
3. Have corresponding test classes added below

Expected model locations:
- mailgun_mcp/models/__init__.py
- mailgun_mcp/models/domain.py
- mailgun_mcp/models/message.py
- mailgun_mcp/models/event.py
- mailgun_mcp/models/template.py
- mailgun_mcp/models/route.py
- mailgun_mcp/models/webhook.py
- mailgun_mcp/models/bounce.py
- mailgun_mcp/models/complaint.py
- mailgun_mcp/models/unsubscribe.py
"""

from __future__ import annotations

import pytest


class TestPydanticModelsAvailability:
    """Test that documents the current state of Pydantic model usage."""

    def test_no_pydantic_models_currently_exist(self) -> None:
        """Verify that the project currently does not use Pydantic models.

        This test documents the current architecture decision to use plain
        dictionaries for API responses. When Pydantic models are introduced,
        this test should be updated or removed.
        """
        # Attempt to import models - they should not exist yet
        try:
            from mailgun_mcp.models import (  # type: ignore[import-not-found]
                Domain,
                Event,
                Message,
                Route,
                Template,
                Webhook,
            )

            # If we get here, models have been added - update tests!
            pytest.skip(
                "Pydantic models have been added. "
                "Remove this test and enable model-specific tests."
            )
        except ImportError:
            # Expected - no models exist yet
            pass

    def test_no_models_directory_exists(self) -> None:
        """Verify that no models directory currently exists.

        This documents the current project structure. When Pydantic models
        are introduced, a models/ directory should be created.
        """
        from pathlib import Path

        models_dir = Path(__file__).parent.parent / "mailgun_mcp" / "models"

        if models_dir.exists():
            pytest.skip(
                "Models directory has been created. "
                "Remove this test and enable model-specific tests."
            )
        # Expected - no models directory exists
        assert not models_dir.exists()

    def test_no_pydantic_dependency(self) -> None:
        """Verify that pydantic is not a project dependency.

        This test documents that the project currently does not require
        Pydantic. When models are added, this test should be removed.
        """
        # Read pyproject.toml to check if pydantic is a direct dependency
        import tomllib
        from pathlib import Path

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject = tomllib.load(f)

            dependencies = pyproject.get("project", {}).get("dependencies", [])
            pydantic_in_deps = any("pydantic" in dep.lower() for dep in dependencies)

            if pydantic_in_deps:
                pytest.skip(
                    "Pydantic has been added as a dependency. "
                    "Remove this test and enable model-specific tests."
                )
            # Expected - pydantic not in dependencies
            assert not pydantic_in_deps


# Template test classes for when Pydantic models are added
# Uncomment and adapt these when models are implemented


class _TemplateDomainModelTests:
    """Template tests for Domain Pydantic model.

    Enable these tests when mailgun_mcp.models.domain.Domain is implemented.
    """

    @pytest.fixture
    def sample_domain_response(self) -> dict:
        """Sample domain API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-domains.html
        """
        return {
            "name": "example.com",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            "wildcard": False,
            "spam_action": "disabled",
            "smtp_password": "super_secret",
            "state": "active",
            "is_disabled": False,
            "type": "custom",
            # Extra fields that Mailgun may add in the future
            "web_prefix": "email",
            "web_scheme": "https",
        }

    @pytest.mark.skip(reason="Domain model not yet implemented")
    def test_extra_fields_ignored(self, sample_domain_response: dict) -> None:
        """Test that the Domain model accepts extra fields without error.

        Pydantic models should use extra='ignore' or extra='allow' in
        model_config to handle unexpected fields from the Mailgun API.
        """
        from mailgun_mcp.models.domain import Domain

        # This should not raise ValidationError
        domain = Domain(**sample_domain_response)

        # Verify expected fields are accessible
        assert domain.name == "example.com"
        assert domain.state == "active"

    @pytest.mark.skip(reason="Domain model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Domain model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.domain import Domain

        # Check model_config
        config = Domain.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Domain model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateMessageModelTests:
    """Template tests for Message/Email Pydantic model.

    Enable these tests when mailgun_mcp.models.message.Message is implemented.
    """

    @pytest.fixture
    def sample_message_response(self) -> dict:
        """Sample message API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-sending.html
        """
        return {
            "id": "<20200101123456.1.ABC123@example.com>",
            "message": "Queued. Thank you.",
            # Extra fields that may be present
            "details": "Message accepted for delivery",
        }

    @pytest.mark.skip(reason="Message model not yet implemented")
    def test_extra_fields_ignored(self, sample_message_response: dict) -> None:
        """Test that the Message model accepts extra fields without error."""
        from mailgun_mcp.models.message import Message

        message = Message(**sample_message_response)
        assert message.id is not None
        assert "Queued" in message.message

    @pytest.mark.skip(reason="Message model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Message model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.message import Message

        config = Message.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Message model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateEventModelTests:
    """Template tests for Event Pydantic model.

    Enable these tests when mailgun_mcp.models.event.Event is implemented.
    """

    @pytest.fixture
    def sample_event_response(self) -> dict:
        """Sample event API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-events.html
        """
        return {
            "id": "ABC123xyz",
            "timestamp": 1577836800.0,
            "event": "delivered",
            "recipient": "user@example.com",
            "message": {
                "headers": {
                    "message-id": "20200101123456.1.ABC123@example.com",
                },
            },
            # Extra fields
            "tags": ["welcome", "transactional"],
            "campaigns": [],
            "user-variables": {},
        }

    @pytest.mark.skip(reason="Event model not yet implemented")
    def test_extra_fields_ignored(self, sample_event_response: dict) -> None:
        """Test that the Event model accepts extra fields without error."""
        from mailgun_mcp.models.event import Event

        event = Event(**sample_event_response)
        assert event.id == "ABC123xyz"
        assert event.event == "delivered"

    @pytest.mark.skip(reason="Event model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Event model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.event import Event

        config = Event.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Event model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateTemplateModelTests:
    """Template tests for Template Pydantic model.

    Enable these tests when mailgun_mcp.models.template.Template is implemented.
    """

    @pytest.fixture
    def sample_template_response(self) -> dict:
        """Sample template API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-templates.html
        """
        return {
            "name": "welcome_email",
            "description": "Welcome email template",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            "version": {
                "tag": "initial",
                "template": "Hello {{name}}, welcome!",
                "engine": "jinja",
                "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
                "comment": "Initial version",
                "active": True,
            },
            # Extra fields
            "id": "template_abc123",
        }

    @pytest.mark.skip(reason="Template model not yet implemented")
    def test_extra_fields_ignored(self, sample_template_response: dict) -> None:
        """Test that the Template model accepts extra fields without error."""
        from mailgun_mcp.models.template import Template

        template = Template(**sample_template_response)
        assert template.name == "welcome_email"

    @pytest.mark.skip(reason="Template model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Template model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.template import Template

        config = Template.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Template model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateRouteModelTests:
    """Template tests for Route Pydantic model.

    Enable these tests when mailgun_mcp.models.route.Route is implemented.
    """

    @pytest.fixture
    def sample_route_response(self) -> dict:
        """Sample route API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-routes.html
        """
        return {
            "id": "route_abc123",
            "priority": 1,
            "expression": "match_recipient('.*@example.com')",
            "action": ["forward('http://example.com/mail')", "stop()"],
            "description": "Forward all example.com mail",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            # Extra fields
            "type": "custom",
        }

    @pytest.mark.skip(reason="Route model not yet implemented")
    def test_extra_fields_ignored(self, sample_route_response: dict) -> None:
        """Test that the Route model accepts extra fields without error."""
        from mailgun_mcp.models.route import Route

        route = Route(**sample_route_response)
        assert route.id == "route_abc123"
        assert route.priority == 1

    @pytest.mark.skip(reason="Route model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Route model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.route import Route

        config = Route.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Route model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateWebhookModelTests:
    """Template tests for Webhook Pydantic model.

    Enable these tests when mailgun_mcp.models.webhook.Webhook is implemented.
    """

    @pytest.fixture
    def sample_webhook_response(self) -> dict:
        """Sample webhook API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-webhooks.html
        """
        return {
            "url": "https://example.com/webhook",
            "type": "delivered",
            # Extra fields
            "id": "webhook_abc123",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
        }

    @pytest.mark.skip(reason="Webhook model not yet implemented")
    def test_extra_fields_ignored(self, sample_webhook_response: dict) -> None:
        """Test that the Webhook model accepts extra fields without error."""
        from mailgun_mcp.models.webhook import Webhook

        webhook = Webhook(**sample_webhook_response)
        assert webhook.url == "https://example.com/webhook"

    @pytest.mark.skip(reason="Webhook model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Webhook model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.webhook import Webhook

        config = Webhook.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Webhook model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateBounceModelTests:
    """Template tests for Bounce Pydantic model.

    Enable these tests when mailgun_mcp.models.bounce.Bounce is implemented.
    """

    @pytest.fixture
    def sample_bounce_response(self) -> dict:
        """Sample bounce API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-suppressions.html#bounces
        """
        return {
            "address": "bounce@example.com",
            "code": 550,
            "error": "User not found",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            # Extra fields
            "type": "Permanent",
        }

    @pytest.mark.skip(reason="Bounce model not yet implemented")
    def test_extra_fields_ignored(self, sample_bounce_response: dict) -> None:
        """Test that the Bounce model accepts extra fields without error."""
        from mailgun_mcp.models.bounce import Bounce

        bounce = Bounce(**sample_bounce_response)
        assert bounce.address == "bounce@example.com"
        assert bounce.code == 550

    @pytest.mark.skip(reason="Bounce model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Bounce model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.bounce import Bounce

        config = Bounce.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Bounce model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateComplaintModelTests:
    """Template tests for Complaint Pydantic model.

    Enable these tests when mailgun_mcp.models.complaint.Complaint is implemented.
    """

    @pytest.fixture
    def sample_complaint_response(self) -> dict:
        """Sample complaint API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-suppressions.html#complaints
        """
        return {
            "address": "complaint@example.com",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            # Extra fields
            "type": "abuse",
        }

    @pytest.mark.skip(reason="Complaint model not yet implemented")
    def test_extra_fields_ignored(self, sample_complaint_response: dict) -> None:
        """Test that the Complaint model accepts extra fields without error."""
        from mailgun_mcp.models.complaint import Complaint

        complaint = Complaint(**sample_complaint_response)
        assert complaint.address == "complaint@example.com"

    @pytest.mark.skip(reason="Complaint model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Complaint model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.complaint import Complaint

        config = Complaint.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Complaint model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


class _TemplateUnsubscribeModelTests:
    """Template tests for Unsubscribe Pydantic model.

    Enable these tests when mailgun_mcp.models.unsubscribe.Unsubscribe is implemented.
    """

    @pytest.fixture
    def sample_unsubscribe_response(self) -> dict:
        """Sample unsubscribe API response from Mailgun.

        Based on Mailgun API documentation:
        https://documentation.mailgun.com/en/latest/api-suppressions.html#unsubscribes
        """
        return {
            "address": "unsub@example.com",
            "tag": "*",
            "created_at": "Tue, 20 Nov 2019 00:00:00 UTC",
            # Extra fields
            "id": "unsub_abc123",
        }

    @pytest.mark.skip(reason="Unsubscribe model not yet implemented")
    def test_extra_fields_ignored(self, sample_unsubscribe_response: dict) -> None:
        """Test that the Unsubscribe model accepts extra fields without error."""
        from mailgun_mcp.models.unsubscribe import Unsubscribe

        unsubscribe = Unsubscribe(**sample_unsubscribe_response)
        assert unsubscribe.address == "unsub@example.com"

    @pytest.mark.skip(reason="Unsubscribe model not yet implemented")
    def test_model_has_extra_ignore(self) -> None:
        """Test that Unsubscribe model_config has extra='ignore' or extra='allow'."""
        from mailgun_mcp.models.unsubscribe import Unsubscribe

        config = Unsubscribe.model_config
        extra_setting = config.get("extra")

        assert extra_setting in ("ignore", "allow"), (
            f"Unsubscribe model should have extra='ignore' or extra='allow', "
            f"got extra='{extra_setting}'"
        )


# Implementation guide for adding Pydantic models
"""
IMPLEMENTATION GUIDE
====================

When ready to add Pydantic models to this project, follow these steps:

1. Create the models directory structure:

   mailgun_mcp/
   └── models/
       ├── __init__.py     # Re-export all models
       ├── domain.py       # Domain model
       ├── message.py      # Message/Email model
       ├── event.py        # Event model
       ├── template.py     # Template model
       ├── route.py        # Route model
       ├── webhook.py      # Webhook model
       ├── bounce.py       # Bounce model
       ├── complaint.py    # Complaint model
       └── unsubscribe.py  # Unsubscribe model

2. Each model should use model_config with extra='ignore':

   from pydantic import BaseModel, ConfigDict

   class Domain(BaseModel):
       model_config = ConfigDict(extra='ignore')

       name: str
       created_at: str
       state: str
       # ... other fields

3. Add pydantic to project dependencies in pyproject.toml

4. Remove the @pytest.mark.skip decorators from the template tests above

5. Remove or update TestPydanticModelsAvailability tests

6. Update main.py to use models for type hints and response parsing

Example model implementation:

   # mailgun_mcp/models/domain.py
   from __future__ import annotations

   from pydantic import BaseModel, ConfigDict
   from typing import Literal

   class Domain(BaseModel):
       model_config = ConfigDict(extra='ignore')

       name: str
       created_at: str
       wildcard: bool = False
       spam_action: Literal["disabled", "block", "tag"] = "disabled"
       smtp_password: str | None = None
       state: Literal["active", "disabled", "unverified"] = "unverified"
       is_disabled: bool = False
       type: Literal["custom", "sandbox"] = "custom"
"""
