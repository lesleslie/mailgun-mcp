import os
from typing import Any

import httpx
from fastmcp import FastMCP
from httpx import BasicAuth

# Initialize FastMCP
mcp = FastMCP(
    name="Mailgun Email Service",
    instructions="A service for sending emails via the Mailgun API",
)


def get_mailgun_api_key() -> str | None:
    return os.environ.get("MAILGUN_API_KEY")


def get_mailgun_domain() -> str | None:
    return os.environ.get("MAILGUN_DOMAIN")


@mcp.tool(
    name="send_message",
    description="Send an email message via Mailgun API",
    output_schema=None,  # Disable automatic serialization so we can return raw values
)
async def send_message(
    from_email: str,
    to: str,
    subject: str,
    text: str,
    cc: str | None = None,
    bcc: str | None = None,
    html: str | None = None,
    attachment: str | None = None,
    tag: str | None = None,
    schedule_at: str | None = None,
) -> dict[str, Any]:
    """Send an email message via Mailgun API"""
    if not get_mailgun_api_key() or not get_mailgun_domain():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables are not set.",
            }
        }

    # Prepare email data
    email_data = {
        "from": from_email,
        "to": to,
        "subject": subject,
        "text": text,
    }

    # Add optional fields if present
    if cc is not None:
        email_data["cc"] = cc
    if bcc is not None:
        email_data["bcc"] = bcc
    if html is not None:
        email_data["html"] = html
    if attachment is not None:
        email_data["attachment"] = attachment
    if tag is not None:
        email_data["o:tag"] = tag
    if schedule_at is not None:
        email_data["o:schedule"] = schedule_at

    # Forward request to Mailgun
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{get_mailgun_domain()}/messages",
            auth=BasicAuth("api", get_mailgun_api_key() or ""),
            data=email_data,
        )

    # Return the response from Mailgun
    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_domains",
    description="Get a list of domains from Mailgun",
    output_schema=None,
)
async def get_domains(limit: int | None = 100, skip: int | None = 0) -> dict[str, Any]:
    """Get a list of domains from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.mailgun.net/v3/domains",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_domain",
    description="Get information about a specific domain from Mailgun",
    output_schema=None,
)
async def get_domain(domain_name: str) -> dict[str, Any]:
    """Get information about a specific domain from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/domains/{domain_name}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="create_domain",
    description="Create a new domain in Mailgun",
    output_schema=None,
)
async def create_domain(
    domain_name: str,
    smtp_password: str,
    spam_action: str | None = "disabled",
    wildcard: bool | None = False,
    ips: str | None = None,
    pool_id: str | None = None,
) -> dict[str, Any]:
    """Create a new domain in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    domain_data = {
        "name": domain_name,
        "smtp_password": smtp_password,
    }

    if spam_action is not None:
        domain_data["spam_action"] = spam_action
    if wildcard is not None:
        domain_data["wildcard"] = str(wildcard).lower()
    if ips is not None:
        domain_data["ips"] = ips
    if pool_id is not None:
        domain_data["pool_id"] = pool_id

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.mailgun.net/v3/domains",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=domain_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_domain", description="Delete a domain from Mailgun", output_schema=None
)
async def delete_domain(domain_name: str) -> dict[str, Any]:
    """Delete a domain from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/domains/{domain_name}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="verify_domain",
    description="Trigger verification of a domain in Mailgun",
    output_schema=None,
)
async def verify_domain(domain_name: str) -> dict[str, Any]:
    """Verify a domain in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.mailgun.net/v3/domains/{domain_name}/verify",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_events",
    description="Get email events (opens, clicks, deliveries, etc.) from Mailgun",
    output_schema=None,
)
async def get_events(
    domain_name: str,
    event: str | None = None,
    begin: str | None = None,
    end: str | None = None,
    ascending: str | None = None,
    limit: int | None = 100,
    pretty: bool | None = True,
) -> dict[str, Any]:
    """Get email events from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "pretty": str(pretty).lower()}

    if event is not None:
        params["event"] = event
    if begin is not None:
        params["begin"] = begin
    if end is not None:
        params["end"] = end
    if ascending is not None:
        params["ascending"] = ascending

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/{domain_name}/events",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_stats",
    description="Get email statistics from Mailgun",
    output_schema=None,
)
async def get_stats(
    domain_name: str,
    event: list[str],
    start: str,
    end: str | None = None,
    resolution: str | None = None,
    duration: str | None = None,
) -> dict[str, Any]:
    """Get email statistics from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"event": event, "start": start}

    if end is not None:
        params["end"] = end
    if resolution is not None:
        params["resolution"] = resolution
    if duration is not None:
        params["duration"] = duration

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/{domain_name}/stats",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_bounces", description="Get email bounces from Mailgun", output_schema=None
)
async def get_bounces(
    domain_name: str, limit: int | None = 100, skip: int | None = 0
) -> dict[str, Any]:
    """Get bounces from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/{domain_name}/bounces",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="add_bounce",
    description="Add an email address to the bounce list in Mailgun",
    output_schema=None,
)
async def add_bounce(
    domain_name: str, address: str, code: int | None = 550, error: str | None = None
) -> dict[str, Any]:
    """Add an email address to bounce list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    bounce_data = {
        "address": address,
    }

    if code is not None:
        bounce_data["code"] = str(code)
    if error is not None:
        bounce_data["error"] = error

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{domain_name}/bounces",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=bounce_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_bounce",
    description="Remove an email address from the bounce list in Mailgun",
    output_schema=None,
)
async def delete_bounce(domain_name: str, address: str) -> dict[str, Any]:
    """Remove an email address from bounce list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/{domain_name}/bounces/{address}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_complaints",
    description="Get email complaints from Mailgun",
    output_schema=None,
)
async def get_complaints(
    domain_name: str, limit: int | None = 100, skip: int | None = 0
) -> dict[str, Any]:
    """Get complaints from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/{domain_name}/complaints",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="add_complaint",
    description="Add an email address to the complaints list in Mailgun",
    output_schema=None,
)
async def add_complaint(domain_name: str, address: str) -> dict[str, Any]:
    """Add an email address to complaints list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    complaint_data = {
        "address": address,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{domain_name}/complaints",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=complaint_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_complaint",
    description="Remove an email address from the complaints list in Mailgun",
    output_schema=None,
)
async def delete_complaint(domain_name: str, address: str) -> dict[str, Any]:
    """Remove an email address from complaints list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/{domain_name}/complaints/{address}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_unsubscribes",
    description="Get unsubscribed email addresses from Mailgun",
    output_schema=None,
)
async def get_unsubscribes(
    domain_name: str, limit: int | None = 100, skip: int | None = 0
) -> dict[str, Any]:
    """Get unsubscribed addresses from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/{domain_name}/unsubscribes",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="add_unsubscribe",
    description="Add an email address to the unsubscribes list in Mailgun",
    output_schema=None,
)
async def add_unsubscribe(
    domain_name: str, address: str, tag: str | None = "*"
) -> dict[str, Any]:
    """Add an email address to unsubscribes list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    unsubscribe_data = {"address": address, "tag": tag}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{domain_name}/unsubscribes",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=unsubscribe_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_unsubscribe",
    description="Remove an email address from the unsubscribes list in Mailgun",
    output_schema=None,
)
async def delete_unsubscribe(
    domain_name: str, address: str, tag: str | None = "*"
) -> dict[str, Any]:
    """Remove an email address from unsubscribes list in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"tag": tag}

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/{domain_name}/unsubscribes/{address}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(name="get_routes", description="Get routes from Mailgun", output_schema=None)
async def get_routes(limit: int | None = 100, skip: int | None = 0) -> dict[str, Any]:
    """Get routes from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.mailgun.net/v3/routes",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_route",
    description="Get a specific route from Mailgun",
    output_schema=None,
)
async def get_route(route_id: str) -> dict[str, Any]:
    """Get a specific route from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/routes/{route_id}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="create_route", description="Create a new route in Mailgun", output_schema=None
)
async def create_route(
    priority: int, expression: str, action: list[str], description: str | None = None
) -> dict[str, Any]:
    """Create a new route in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    route_data = {
        "priority": str(priority),  # type: ignore
        "expression": expression,
        "action": action,  # type: ignore
    }

    if description is not None:
        route_data["description"] = description

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.mailgun.net/v3/routes",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=route_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="update_route",
    description="Update an existing route in Mailgun",
    output_schema=None,
)
async def update_route(
    route_id: str,
    priority: int | None = None,
    expression: str | None = None,
    action: list[str] | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update an existing route in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    route_data = {}

    if priority is not None:
        route_data["priority"] = priority  # type: ignore
    if expression is not None:
        route_data["expression"] = expression  # type: ignore
    if action is not None:
        route_data["action"] = action  # type: ignore
    if description is not None:
        route_data["description"] = description  # type: ignore

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.mailgun.net/v3/routes/{route_id}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=route_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_route", description="Delete a route from Mailgun", output_schema=None
)
async def delete_route(route_id: str) -> dict[str, Any]:
    """Delete a route from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/routes/{route_id}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_templates",
    description="Get a list of templates from Mailgun",
    output_schema=None,
)
async def get_templates(
    limit: int | None = 100, skip: int | None = 0
) -> dict[str, Any]:
    """Get a list of templates from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    params = {"limit": limit, "skip": skip}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.mailgun.net/v3/templates",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            params=params,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_template",
    description="Get information about a specific template from Mailgun",
    output_schema=None,
)
async def get_template(template_name: str) -> dict[str, Any]:
    """Get information about a specific template from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/templates/{template_name}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="create_template",
    description="Create a new template in Mailgun",
    output_schema=None,
)
async def create_template(
    name: str,
    subject: str,
    template_text: str,
    template_html: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new template in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    template_data = {
        "name": name,
        "subject": subject,
        "template": template_text,
    }

    if template_html is not None:
        template_data["html"] = template_html
    if description is not None:
        template_data["description"] = description

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.mailgun.net/v3/templates",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=template_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="update_template",
    description="Update an existing template in Mailgun",
    output_schema=None,
)
async def update_template(
    template_name: str,
    description: str | None = None,
    template_version_name: str | None = None,
    template_version_subject: str | None = None,
    template_version_template: str | None = None,
    template_version_html: str | None = None,
    template_version_active: bool | None = None,
) -> dict[str, Any]:
    """Update an existing template in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    template_data = {}

    if description is not None:
        template_data["description"] = description
    if template_version_name is not None:
        template_data["name"] = template_version_name
    if template_version_subject is not None:
        template_data["subject"] = template_version_subject
    if template_version_template is not None:
        template_data["template"] = template_version_template
    if template_version_html is not None:
        template_data["html"] = template_version_html
    if template_version_active is not None:
        template_data["active"] = str(template_version_active).lower()

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.mailgun.net/v3/templates/{template_name}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=template_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_template",
    description="Delete a template from Mailgun",
    output_schema=None,
)
async def delete_template(template_name: str) -> dict[str, Any]:
    """Delete a template from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/templates/{template_name}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_webhooks", description="Get all webhooks from Mailgun", output_schema=None
)
async def get_webhooks() -> dict[str, Any]:
    """Get all webhooks from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.mailgun.net/v3/domains/webhooks",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="get_webhook",
    description="Get a specific webhook from Mailgun",
    output_schema=None,
)
async def get_webhook(webhook_type: str) -> dict[str, Any]:
    """Get a specific webhook from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mailgun.net/v3/domains/webhooks/{webhook_type}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="create_webhook",
    description="Create or update a webhook in Mailgun",
    output_schema=None,
)
async def create_webhook(webhook_type: str, url: str) -> dict[str, Any]:
    """Create or update a webhook in Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    webhook_data = {"url": url}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/domains/webhooks/{webhook_type}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
            data=webhook_data,
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


@mcp.tool(
    name="delete_webhook",
    description="Delete a webhook from Mailgun",
    output_schema=None,
)
async def delete_webhook(webhook_type: str) -> dict[str, Any]:
    """Delete a webhook from Mailgun API"""
    if not get_mailgun_api_key():
        return {
            "error": {
                "type": "configuration_error",
                "message": "MAILGUN_API_KEY environment variable is not set.",
            }
        }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.mailgun.net/v3/domains/webhooks/{webhook_type}",
            auth=BasicAuth("api", get_mailgun_api_key()),  # type: ignore
        )

    if response.is_success:
        return response.json()  # type: ignore
    return {
        "error": {
            "type": "mailgun_error",
            "message": f"Mailgun request failed with status {response.status_code}",
            "details": response.text,
        }
    }


# Export the application for uvicorn
app = mcp.http_app
