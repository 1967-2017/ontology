from __future__ import annotations

from typing import Any


def sanitize_unicode_payload(value: Any) -> Any:
    if isinstance(value, str):
        return _strip_surrogates(value)
    if isinstance(value, list):
        return [sanitize_unicode_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_unicode_payload(item) for key, item in value.items()}
    return value


def _strip_surrogates(value: str) -> str:
    return value.encode("utf-8", "surrogatepass").decode("utf-8", "ignore")
