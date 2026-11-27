from pathlib import Path

from foodlog import images


def test_meal_from_name():
    assert images.meal_from_name(Path("2026-06-20 lunch.jpg")) == "lunch"
    assert images.meal_from_name(Path("2026-06-20 Dinner.heic")) == "dinner"
    assert images.meal_from_name(Path("2026-06-20 1330.jpg")) == ""


def test_read_sidecar_note(tmp_path):
    img = tmp_path / "meal.jpg"
    img.write_bytes(b"")
    (tmp_path / "meal.txt").write_text("  chicken rice  ")
    assert images.read_sidecar_note(img) == "chicken rice"


def test_read_sidecar_note_absent(tmp_path):
    img = tmp_path / "meal.jpg"
    img.write_bytes(b"")
    assert images.read_sidecar_note(img) == ""


def test_unique_name(tmp_path):
    assert images.unique_name(tmp_path, "2026-06-20 lunch", ".jpg") == "2026-06-20 lunch.jpg"
    (tmp_path / "2026-06-20 lunch.jpg").write_bytes(b"")
    assert images.unique_name(tmp_path, "2026-06-20 lunch", ".jpg") == "2026-06-20 lunch 2.jpg"
    (tmp_path / "2026-06-20 lunch 2.jpg").write_bytes(b"")
    assert images.unique_name(tmp_path, "2026-06-20 lunch", ".jpg") == "2026-06-20 lunch 3.jpg"
