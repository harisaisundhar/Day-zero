"""Tests for summary.md rendering/parsing (the pure data layer)."""

from foodlog import summary
from foodlog.models import Meal


def _meal(meal="lunch", kcal=200, items="Rice (1 cup)", date="2026-06-20"):
    return Meal(date=date, time="12:30", meal=meal, file="x.jpg", items=items,
                kcal=kcal, protein_g=4, carbs_g=44, fat_g=1,
                confidence="med", note="", src_note="")


def test_render_then_parse_roundtrip():
    meals = [_meal(), _meal(meal="dinner", kcal=500, items="Dosa (1)")]
    text = summary.render(meals, target=2400)
    loaded = summary.parse(text)
    assert len(loaded) == 2
    assert {m.meal for m in loaded} == {"lunch", "dinner"}
    assert sum(m.kcal for m in loaded) == 700


def test_parse_empty_text():
    assert summary.parse("# nothing here") == []


def test_human_view_has_day_total_and_macros():
    text = summary.render([_meal(kcal=300), _meal(meal="dinner", kcal=400)],
                          target=2400)
    assert "~700 kcal" in text          # day total
    assert "8P / 88C / 2F" in text       # macros summed
    assert "✅ under 2400" in text


def test_over_target_flag():
    text = summary.render([_meal(kcal=300)], target=100)
    assert "⚠️ over 100" in text


def test_accumulates_across_renders():
    """Simulate two daily runs: parse, append, render — nothing lost."""
    text = summary.render([_meal(meal="breakfast", kcal=330)])
    rows = summary.parse(text)
    rows.append(_meal(meal="lunch", kcal=710))
    text2 = summary.render(rows)
    assert len(summary.parse(text2)) == 2
