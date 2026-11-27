"""Domain models for FoodLog."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

from . import config


@dataclass
class Meal:
    """One logged meal — the unit persisted in summary.md's data block."""

    date: str          # "YYYY-MM-DD"
    time: str          # "HH:MM"
    meal: str          # breakfast | lunch | dinner | snack
    file: str          # archived photo filename
    items: str         # "Item (portion); Item (portion)"
    kcal: int
    protein_g: int
    carbs_g: int
    fat_g: int
    confidence: str    # low | med | high
    note: str          # model's assumption note
    src_note: str      # the user's note from the phone

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Meal":
        # Tolerate older/partial rows by filling defaults.
        return cls(
            date=d.get("date", ""),
            time=d.get("time", ""),
            meal=d.get("meal", "snack"),
            file=d.get("file", ""),
            items=d.get("items", ""),
            kcal=int(d.get("kcal", 0) or 0),
            protein_g=int(d.get("protein_g", 0) or 0),
            carbs_g=int(d.get("carbs_g", 0) or 0),
            fat_g=int(d.get("fat_g", 0) or 0),
            confidence=d.get("confidence", "low"),
            note=d.get("note", ""),
            src_note=d.get("src_note", ""),
        )


def meal_type_for(when: datetime) -> str:
    """Classify a meal by the photo's capture hour."""
    for name, start, end in config.MEAL_WINDOWS:
        if start <= when.hour < end:
            return name
    return "snack"
