"""Orchestration: pull pending photos from a backend, estimate, archive, log.

Backend-agnostic: works with the local (Mac/iCloud) backend or the Google Drive
(cloud) backend. Idempotent + crash-safe: a photo is archived only AFTER its
meal row has been recorded, so re-running never double-counts or loses a meal.
"""

from __future__ import annotations

import logging

from . import config, images
from .backends import Backend, InboxItem, get_backend
from .estimators import Estimator, get_estimator
from .models import Meal, meal_type_for

log = logging.getLogger("foodlog")


def run() -> int:
    """Process all pending photos. Returns a process exit code."""
    backend = get_backend(config.BACKEND)
    estimator = get_estimator(config.ESTIMATOR)
    meals = backend.load_summary()

    pending = backend.list_inbox()
    if not pending:
        log.info("inbox empty — nothing to do")
        if meals:
            backend.save_summary(meals)  # keep summary fresh
        return 0

    log.info("found %d photo(s); backend=%s estimator=%s",
             len(pending), config.BACKEND, config.ESTIMATOR)

    ok = 0
    for item in pending:
        try:
            meals.append(_process_one(item, backend, estimator))
            ok += 1
        except Exception as e:  # noqa: BLE001 — keep going; leave item for retry
            log.error("ERROR on %s: %s — left in inbox for retry", item.name, e)

    backend.save_summary(meals)
    if hasattr(backend, "cleanup"):
        backend.cleanup()
    log.info("done: %d/%d logged", ok, len(pending))
    return 0


def _process_one(item: InboxItem, backend: Backend, estimator: Estimator) -> Meal:
    from pathlib import Path

    when = item.captured_at
    est = estimator.estimate(item.image, item.mime_type, item.src_note)
    meal_name = images.meal_from_name(Path(item.name)) or meal_type_for(when)

    base = f"{when:%Y-%m-%d} {meal_name}"
    # Archive AFTER estimation; backend resolves any name collision and returns
    # the final archived filename (crash-safe ordering: move happens here).
    archived = backend.archive(item, base)

    return Meal(
        date=when.strftime("%Y-%m-%d"),
        time=when.strftime("%H:%M"),
        meal=meal_name,
        file=archived,
        items=est["items"],
        kcal=est["kcal"],
        protein_g=est["protein_g"],
        carbs_g=est["carbs_g"],
        fat_g=est["fat_g"],
        confidence=est["confidence"],
        note=est["note"],
        src_note=item.src_note,
    )
