"""Configuration for FoodLog.

All settings live here and can be overridden by environment variables so that
secrets (e.g. the Gemini API key) never need to be committed to the repo.

Layout philosophy: CODE and PHOTOS are separated.
  - REPO_DIR   : this git repo (code + local photo archive), kept out of iCloud.
  - ICLOUD_DIR : iCloud Drive folder the iPhone Shortcut writes into; holds the
                 inbox/ of incoming photos and summary.md (viewable on phone).
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Behaviour ---
DAILY_TARGET_KCAL: int = int(os.environ.get("FOODLOG_TARGET_KCAL", "2400"))

# Which estimator to use: "gemini" or "claude".
ESTIMATOR: str = os.environ.get("FOODLOG_ESTIMATOR", "gemini")

# Where photos + the log live. Currently only "local" (Mac/iCloud + launchd).
BACKEND: str = os.environ.get("FOODLOG_BACKEND", "local")

# --- Gemini API (ESTIMATOR == "gemini") ---
# Prefer a PERSONAL Google AI Studio key (starts with "AIza..."), NOT a
# corporate GCP/Vertex credential. Get one free at:
#   https://aistudio.google.com/apikey
# Set it via the GEMINI_API_KEY env var (recommended) to keep it out of git.
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.environ.get("FOODLOG_GEMINI_MODEL", "gemini-2.0-flash")

# --- claude CLI (ESTIMATOR == "claude") ---
CLAUDE_BIN: str = os.environ.get(
    "FOODLOG_CLAUDE_BIN",
    str(Path.home() / ".local/bin/claude"),
)

# --- Locations ---
REPO_DIR: Path = Path(__file__).resolve().parents[2]
ICLOUD_DIR: Path = Path(
    os.environ.get(
        "FOODLOG_ICLOUD_DIR",
        str(Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/FoodLog"),
    )
)

INBOX_DIR: Path = ICLOUD_DIR / "inbox"        # phone drops photos here (iCloud)
SUMMARY_PATH: Path = ICLOUD_DIR / "summary.md"  # glanceable log (iCloud)
ARCHIVE_DIR: Path = REPO_DIR / "done"         # archived photos (local only)

# --- Constants ---
IMAGE_EXTS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
)
JPEG_EXTS: frozenset[str] = frozenset({".jpg", ".jpeg", ".png"})

# Meal windows (start_hour, end_hour) in 24h time; outside all of these = snack.
MEAL_WINDOWS: tuple[tuple[str, int, int], ...] = (
    ("breakfast", 5, 9),
    ("lunch", 11, 14),
    ("dinner", 18, 21),
)
MEAL_ORDER: tuple[str, ...] = ("breakfast", "lunch", "dinner", "snack")

# Marker for the hidden, machine-readable JSON block inside summary.md.
DATA_MARKER: str = "<!-- FOODLOG-DATA"
