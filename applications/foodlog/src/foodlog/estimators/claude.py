"""Claude estimator — calls the local `claude` CLI in headless mode.

The CLI reads an image from a path, so we write the bytes to a temp file first.
Only usable on a machine with the claude CLI installed (i.e. the local backend).
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .. import config
from ..prompt import build_prompt
from . import extract_json, normalize

_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


class ClaudeEstimator:
    def __init__(self, claude_bin: str | None = None):
        self.claude_bin = claude_bin or config.CLAUDE_BIN

    def estimate(self, image: bytes, mime_type: str, src_note: str) -> dict:
        suffix = _EXT.get(mime_type, ".jpg")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(image)
            tmp.flush()
            prompt = (
                build_prompt(src_note)
                + "\n\nAnalyze the food in this image file and return ONLY the "
                f"JSON object.\nImage path: {tmp.name}\n"
            )
            res = subprocess.run(
                [self.claude_bin, "-p", prompt, "--allowedTools", "Read"],
                capture_output=True, text=True, timeout=180,
            )
        if res.returncode != 0:
            raise RuntimeError(f"claude failed: {res.stderr[:300]}")
        return normalize(extract_json(res.stdout))
