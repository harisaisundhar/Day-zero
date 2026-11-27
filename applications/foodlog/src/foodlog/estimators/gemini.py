"""Gemini estimator — calls the Google AI Studio Generative Language API.

Uses a PERSONAL AI Studio key (starts with 'AIza...'). Stdlib only.
"""

from __future__ import annotations

import base64
import json
import urllib.request

from .. import config
from ..prompt import build_prompt
from . import extract_json, normalize

_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)


class GeminiEstimator:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or config.GEMINI_MODEL

    def estimate(self, image: bytes, mime_type: str, src_note: str) -> dict:
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set — export it or set it in config."
            )
        prompt = build_prompt(src_note) + "\nReturn ONLY the JSON object."
        body = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {
                        "mime_type": mime_type,
                        "data": base64.b64encode(image).decode(),
                    }},
                ]
            }],
            "generationConfig": {"response_mime_type": "application/json"},
        }
        url = _ENDPOINT.format(model=self.model, key=self.api_key)
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            out = json.loads(resp.read().decode())
        text = out["candidates"][0]["content"]["parts"][0]["text"]
        return normalize(extract_json(text))
