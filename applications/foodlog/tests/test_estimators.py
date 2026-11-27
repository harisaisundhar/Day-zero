import pytest

from foodlog import estimators


def test_extract_json_from_noisy_text():
    assert estimators.extract_json('blah {"a": 1} trailing') == {"a": 1}


def test_extract_json_missing_raises():
    with pytest.raises(ValueError):
        estimators.extract_json("no json here")


def test_normalize_items_as_dicts():
    raw = {
        "items": [
            {"name": "Idli", "portion": "2 pcs"},
            {"name": "Sambar", "portion": "1 bowl"},
        ],
        "total_kcal": 140.4, "total_protein_g": 4,
        "total_carbs_g": 28, "total_fat_g": 1, "confidence": "high",
        "note": "ok",
    }
    out = estimators.normalize(raw)
    assert out["items"] == "Idli (2 pcs); Sambar (1 bowl)"
    assert out["kcal"] == 140        # rounded from float
    assert out["confidence"] == "high"


def test_normalize_items_as_strings():
    out = estimators.normalize({"items": ["Coffee"], "total_kcal": 90})
    assert out["items"] == "Coffee"
    assert out["kcal"] == 90
    assert out["confidence"] == "low"   # default


def test_normalize_handles_missing_fields():
    out = estimators.normalize({})
    assert out == {"items": "", "kcal": 0, "protein_g": 0, "carbs_g": 0,
                   "fat_g": 0, "confidence": "low", "note": ""}


def test_get_estimator_unknown():
    with pytest.raises(ValueError):
        estimators.get_estimator("nope")
