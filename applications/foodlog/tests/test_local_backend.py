"""Local backend tests that don't require macOS sips (use plain .jpg/.png)."""

from datetime import datetime

import pytest

from foodlog import config
from foodlog.backends import InboxItem
from foodlog.backends.local import LocalBackend


@pytest.fixture
def backend(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    archive = tmp_path / "done"
    inbox.mkdir()
    monkeypatch.setattr(config, "INBOX_DIR", inbox)
    monkeypatch.setattr(config, "ARCHIVE_DIR", archive)
    monkeypatch.setattr(config, "SUMMARY_PATH", tmp_path / "summary.md")
    return LocalBackend(), inbox, archive


def test_list_inbox_reads_image_and_note(backend):
    be, inbox, _ = backend
    (inbox / "2026-06-20 1300.jpg").write_bytes(b"\xff\xd8\xff")  # tiny jpeg-ish
    (inbox / "2026-06-20 1300.txt").write_text("two idli")
    items = be.list_inbox()
    assert len(items) == 1
    assert items[0].src_note == "two idli"
    assert items[0].image == b"\xff\xd8\xff"


def test_archive_moves_and_dedupes(backend):
    be, inbox, archive = backend
    (inbox / "a.png").write_bytes(b"x")
    item = be.list_inbox()[0]
    item.captured_at = datetime(2026, 6, 20, 13, 0)
    item.suffix = ".png"
    item.extra["src_path"] = inbox / "a.png"

    name1 = be.archive(item, "2026-06-20 lunch")
    assert name1 == "2026-06-20 lunch.png"
    assert (archive / "2026-06-20" / name1).exists()

    # second item same day+meal -> deduped name
    (inbox / "b.png").write_bytes(b"y")
    item2 = InboxItem(name="b.png", image=b"y", mime_type="image/png",
                      captured_at=datetime(2026, 6, 20, 13, 5), suffix=".png",
                      extra={"src_path": inbox / "b.png"})
    name2 = be.archive(item2, "2026-06-20 lunch")
    assert name2 == "2026-06-20 lunch 2.png"


def test_summary_roundtrip(backend):
    from foodlog.models import Meal
    be, _, _ = backend
    assert be.load_summary() == []
    meal = Meal(date="2026-06-20", time="13:00", meal="lunch", file="x.png",
                items="Idli (2)", kcal=200, protein_g=6, carbs_g=36, fat_g=2,
                confidence="low", note="", src_note="")
    be.save_summary([meal])
    assert len(be.load_summary()) == 1
