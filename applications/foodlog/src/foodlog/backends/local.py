"""Local filesystem backend (Mac + iCloud), used with launchd.

Inbox + summary.md live in iCloud; the photo archive lives in the local repo.
HEIC->JPEG and EXIF dates use macOS `sips` via images.py.
"""

from __future__ import annotations

import mimetypes
import shutil
from pathlib import Path

from .. import config, images, summary
from ..models import Meal
from . import InboxItem


class LocalBackend:
    def __init__(self):
        self.inbox = config.INBOX_DIR
        self.archive_dir = config.ARCHIVE_DIR
        self.summary_path = config.SUMMARY_PATH

    def list_inbox(self) -> list[InboxItem]:
        self.inbox.mkdir(parents=True, exist_ok=True)
        items: list[InboxItem] = []
        work = self.archive_dir / "_work"
        for p in sorted(self.inbox.iterdir()):
            if not (p.is_file() and p.suffix.lower() in config.IMAGE_EXTS):
                continue
            jpeg = images.to_jpeg(p, work)  # convert HEIC etc for the model
            mime = mimetypes.guess_type(str(jpeg))[0] or "image/jpeg"
            items.append(InboxItem(
                name=p.name,
                image=Path(jpeg).read_bytes(),
                mime_type=mime,
                src_note=images.read_sidecar_note(p),
                captured_at=images.capture_date(p),
                suffix=p.suffix,
                extra={"src_path": p},
            ))
        return items

    def archive(self, item: InboxItem, base: str) -> str:
        when = item.captured_at
        day_dir = self.archive_dir / when.strftime("%Y-%m-%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        archived_name = images.unique_name(day_dir, base, item.suffix)
        src: Path = item.extra["src_path"]
        shutil.move(str(src), str(day_dir / archived_name))
        sidecar = src.with_suffix(".txt")
        if sidecar.exists():
            shutil.move(str(sidecar),
                        str(day_dir / Path(archived_name).with_suffix(".txt").name))
        return archived_name

    def load_summary(self) -> list[Meal]:
        if not self.summary_path.exists():
            return []
        return summary.parse(self.summary_path.read_text())

    def save_summary(self, meals: list[Meal]) -> None:
        self.summary_path.parent.mkdir(parents=True, exist_ok=True)
        self.summary_path.write_text(summary.render(meals))

    def cleanup(self) -> None:
        work = self.archive_dir / "_work"
        if work.exists():
            shutil.rmtree(work, ignore_errors=True)
