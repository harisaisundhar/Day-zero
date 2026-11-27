"""Storage backends: where photos and the log live.

A backend hides whether we're on the local Mac/iCloud filesystem or in Google
Drive. The pipeline depends only on this interface, so adding a new store (S3,
Dropbox, ...) is one new module.

An InboxItem represents one pending photo plus its optional note.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from ..models import Meal


@dataclass
class InboxItem:
    name: str                     # original filename (for meal/date hints)
    image: bytes                  # raw image bytes
    mime_type: str                # e.g. "image/jpeg"
    src_note: str = ""            # optional note from the phone
    captured_at: datetime | None = None  # EXIF/known capture time, if available
    suffix: str = ".jpg"          # original extension (for the archive name)
    extra: dict = field(default_factory=dict)  # backend-private handles (ids…)


class Backend(Protocol):
    def list_inbox(self) -> list[InboxItem]: ...
    # Move the item into the archive under <base><suffix>, resolving any name
    # collision. Returns the final archived filename.
    def archive(self, item: InboxItem, base: str) -> str: ...
    def load_summary(self) -> list[Meal]: ...
    def save_summary(self, meals: list[Meal]) -> None: ...


def get_backend(name: str) -> Backend:
    """Return a backend instance by name ('local')."""
    if name == "local":
        from .local import LocalBackend
        return LocalBackend()
    raise ValueError(f"unknown backend: {name!r} (use 'local')")
