"""Image and filesystem helpers: EXIF dates, HEIC->JPEG, notes, naming.

Uses macOS's built-in `sips` for metadata and conversion (no Pillow dependency).
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from . import config


def capture_date(path: Path) -> datetime:
    """Photo capture time from EXIF (via sips), falling back to file mtime."""
    try:
        out = subprocess.run(
            ["sips", "-g", "creation", str(path)],
            capture_output=True, text=True, timeout=20,
        ).stdout
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("creation:"):
                val = line.split("creation:", 1)[1].strip()
                return datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def to_jpeg(path: Path, work_dir: Path) -> Path:
    """Return a JPEG/PNG path the model can read, converting HEIC/etc via sips."""
    if path.suffix.lower() in config.JPEG_EXTS:
        return path
    work_dir.mkdir(parents=True, exist_ok=True)
    out = work_dir / (path.stem + ".jpg")
    subprocess.run(
        ["sips", "-s", "format", "jpeg", str(path), "--out", str(out)],
        capture_output=True, text=True, timeout=60, check=True,
    )
    return out


def read_sidecar_note(img: Path) -> str:
    """Read the optional note the Shortcut saved as a sidecar .txt."""
    sidecar = img.with_suffix(".txt")
    if sidecar.exists():
        try:
            return sidecar.read_text().strip()
        except OSError:
            pass
    return ""


def meal_from_name(path: Path) -> str:
    """If the filename already names the meal (e.g. '... lunch.jpg'), use it."""
    stem = path.stem.lower()
    for name in config.MEAL_ORDER:
        if name in stem:
            return name
    return ""


def unique_name(folder: Path, base: str, suffix: str) -> str:
    """'base.suffix', or 'base 2.suffix', 'base 3.suffix'... if already taken."""
    if not (folder / f"{base}{suffix}").exists():
        return f"{base}{suffix}"
    n = 2
    while (folder / f"{base} {n}{suffix}").exists():
        n += 1
    return f"{base} {n}{suffix}"
