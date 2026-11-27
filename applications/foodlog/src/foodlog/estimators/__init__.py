"""Estimator backends and a factory to select one.

An estimator takes raw image bytes (+ mime type) and an optional note, and
returns a normalized nutrition dict:

    {"items": str, "kcal": int, "protein_g": int, "carbs_g": int,
     "fat_g": int, "confidence": str, "note": str}

Working on bytes (not paths) lets the same estimator serve both the local
filesystem backend and the Google Drive backend.
"""

from __future__ import annotations

import json
from typing import Protocol


class Estimator(Protocol):
    def estimate(self, image: bytes, mime_type: str, src_note: str) -> dict: ...


def get_estimator(name: str) -> Estimator:
    """Return an estimator instance by name ('gemini' or 'claude')."""
    if name == "gemini":
        from .gemini import GeminiEstimator
        return GeminiEstimator()
    if name == "claude":
        from .claude import ClaudeEstimator
        return ClaudeEstimator()
    raise ValueError(f"unknown estimator: {name!r} (use 'gemini' or 'claude')")


# --- shared parsing helpers used by every backend ---
def extract_json(text: str) -> dict:
    """Extract the first JSON object from a model response."""
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object in response: {text[:200]!r}")
    return json.loads(text[start:end + 1])


def _to_int(v) -> int:
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return 0


def normalize(raw: dict) -> dict:
    """Turn a raw model JSON object into the normalized nutrition dict."""
    items = raw.get("items", [])
    if isinstance(items, dict):
        items = [items]
    names: list[str] = []
    for it in items if isinstance(items, list) else []:
        if isinstance(it, str):
            names.append(it)
        elif isinstance(it, dict):
            nm = it.get("name") or it.get("item") or it.get("food") or "item"
            portion = it.get("portion") or ""
            names.append(f"{nm} ({portion})" if portion else str(nm))
    return {
        "items": "; ".join(names),
        "kcal": _to_int(raw.get("total_kcal")),
        "protein_g": _to_int(raw.get("total_protein_g")),
        "carbs_g": _to_int(raw.get("total_carbs_g")),
        "fat_g": _to_int(raw.get("total_fat_g")),
        "confidence": raw.get("confidence", "low"),
        "note": raw.get("note", ""),
    }
