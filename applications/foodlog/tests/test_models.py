from datetime import datetime

from foodlog.models import Meal, meal_type_for


def test_meal_type_windows():
    assert meal_type_for(datetime(2026, 6, 20, 7, 0)) == "breakfast"
    assert meal_type_for(datetime(2026, 6, 20, 12, 30)) == "lunch"
    assert meal_type_for(datetime(2026, 6, 20, 19, 0)) == "dinner"
    # outside all windows -> snack
    assert meal_type_for(datetime(2026, 6, 20, 16, 0)) == "snack"
    assert meal_type_for(datetime(2026, 6, 20, 23, 0)) == "snack"


def test_meal_window_boundaries():
    # windows are [start, end)
    assert meal_type_for(datetime(2026, 6, 20, 5, 0)) == "breakfast"
    assert meal_type_for(datetime(2026, 6, 20, 9, 0)) == "snack"  # end exclusive


def test_meal_roundtrip():
    m = Meal(
        date="2026-06-20", time="12:30", meal="lunch", file="x.jpg",
        items="Rice (1 cup)", kcal=200, protein_g=4, carbs_g=44, fat_g=1,
        confidence="med", note="n", src_note="s",
    )
    assert Meal.from_dict(m.to_dict()) == m


def test_meal_from_partial_dict():
    m = Meal.from_dict({"date": "2026-06-20", "kcal": "300"})
    assert m.kcal == 300
    assert m.meal == "snack"
    assert m.protein_g == 0
