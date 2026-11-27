"""Pure rendering/parsing of summary.md (no I/O).

summary.md has two parts:
  1. A human-readable markdown view (grouped by day and meal).
  2. A hidden machine-readable JSON block inside an HTML comment, read back to
     accumulate across runs (so no separate database/CSV is needed).

Backends own the actual reading/writing of the text; this module just converts
between the text and a list of Meal objects.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from . import config
from .models import Meal


def parse(text: str) -> list[Meal]:
    """Extract meals from the hidden data block of a summary.md string."""
    i = text.find(config.DATA_MARKER)
    if i == -1:
        return []
    block = text[i + len(config.DATA_MARKER):]
    if "-->" in block:
        block = block[:block.find("-->")]
    start = block.find("[")  # JSON array begins after the marker prose
    if start == -1:
        return []
    try:
        data = json.loads(block[start:].strip())
    except (json.JSONDecodeError, ValueError):
        return []
    return [Meal.from_dict(d) for d in data]


def render(meals: list[Meal], target: int | None = None) -> str:
    """Render meals into the full summary.md text (view + hidden data block)."""
    target = target if target is not None else config.DAILY_TARGET_KCAL
    by_day: dict[str, dict[str, int]] = defaultdict(
        lambda: {"kcal": 0, "p": 0, "c": 0, "f": 0}
    )
    by_meal: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {"kcal": 0, "items": []})
    )
    for m in meals:
        d = by_day[m.date]
        d["kcal"] += m.kcal
        d["p"] += m.protein_g
        d["c"] += m.carbs_g
        d["f"] += m.fat_g
        cell = by_meal[m.date][m.meal]
        cell["kcal"] += m.kcal
        if m.items:
            cell["items"].append(m.items)

    out = [
        "# Calorie Log",
        "",
        f"_Target ~{target} kcal/day · approximate · auto-generated_",
        "",
    ]
    for day in sorted(by_day, reverse=True):
        d = by_day[day]
        flag = "✅ under" if d["kcal"] <= target else "⚠️ over"
        try:
            pretty = datetime.strptime(day, "%Y-%m-%d").strftime("%a %b %d")
        except ValueError:
            pretty = day
        out.append(
            f"### {pretty} — ~{d['kcal']} kcal · "
            f"{d['p']}P / {d['c']}C / {d['f']}F · {flag} {target}"
        )
        for meal_name in config.MEAL_ORDER:
            if meal_name in by_meal[day]:
                cell = by_meal[day][meal_name]
                out.append(
                    f"- **{meal_name.capitalize()}** (~{cell['kcal']} kcal): "
                    f"{'; '.join(cell['items'])}"
                )
        out.append("")

    out += [
        config.DATA_MARKER + " — do not edit below this line",
        json.dumps([m.to_dict() for m in meals], ensure_ascii=False),
        "-->",
        "",
    ]
    return "\n".join(out)
