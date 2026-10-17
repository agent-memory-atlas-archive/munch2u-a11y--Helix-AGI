"""Shared bounded state contract for the dashboard and canvas tool."""
from __future__ import annotations

import json
import math
import time

VIEW_TYPES = frozenset({
    "markdown", "text", "image", "media", "browser", "iframe",
    "terminal", "sandbox", "card", "alert",
})
MAX_CANVAS_BYTES = 1_000_000


def normalize_canvas_payload(data):
    if not isinstance(data, dict):
        raise ValueError("Canvas payload must be a JSON object")
    kind = data.get("view_type", "card")
    if not isinstance(kind, str) or kind.strip().lower() not in VIEW_TYPES:
        raise ValueError("Unsupported canvas view_type")
    payload = {"view_type": kind.strip().lower()}
    for key, default in (("title", "Agent Canvas"), ("content", "")):
        value = data.get(key, default)
        if not isinstance(value, str):
            raise ValueError(f"Canvas {key} must be text")
        payload[key] = value.strip()
    media = data.get("media_url")
    if media is not None and not isinstance(media, str):
        raise ValueError("Canvas media_url must be text or null")
    payload["media_url"] = media.strip() if media else None
    switch = data.get("auto_switch", False)
    if not isinstance(switch, bool):
        raise ValueError("Canvas auto_switch must be boolean")
    payload["auto_switch"] = switch
    timestamp = data.get("timestamp", time.time())
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise ValueError("Canvas timestamp must be a finite number")
    try:
        finite = math.isfinite(timestamp)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("Canvas timestamp must be a finite number")
    payload["timestamp"] = timestamp
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("Canvas metadata must be an object")
    payload["metadata"] = metadata
    try:
        encoded = json.dumps(payload, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("Canvas metadata must contain finite JSON values") from exc
    if len(encoded) > MAX_CANVAS_BYTES:
        raise ValueError(f"Canvas payload exceeds {MAX_CANVAS_BYTES} bytes")
    return payload
