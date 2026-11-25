"""Explicit tenant-scoped local LMS launch; no token or grade synchronization."""
import os
from urllib.parse import urlsplit
from uuid import UUID


def moodle_link(tenant_id: str) -> dict:
    disabled = {"enabled": False}
    configured = os.environ.get("MOODLE_TENANT_ID", "")
    url = os.environ.get("MOODLE_URL", "")
    try:
        if str(UUID(configured)) != str(UUID(tenant_id)):
            return disabled
        parsed = urlsplit(url)
        if (parsed.scheme != "http" or parsed.hostname != "localhost"
                or parsed.username or parsed.password or not parsed.port
                or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
            return disabled
    except (ValueError, TypeError):
        return disabled
    return {"enabled": True, "url": url.rstrip("/") + "/",
            "scope": "single-organization local pilot", "progress_sync": False}
