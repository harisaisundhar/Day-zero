"""Command-line entry point for FoodLog."""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__, config
from .pipeline import run


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="foodlog",
        description="Estimate calories+macros from food photos and log them.",
    )
    parser.add_argument("--version", action="version",
                        version=f"foodlog {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable debug logging")
    parser.add_argument("--show-config", action="store_true",
                        help="print resolved paths/settings and exit")
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    if args.show_config:
        print(f"backend     : {config.BACKEND}")
        print(f"estimator   : {config.ESTIMATOR}")
        print(f"target kcal : {config.DAILY_TARGET_KCAL}")
        print(f"gemini key  : {'set' if config.GEMINI_API_KEY else 'NOT set'}")
        if config.BACKEND == "local":
            print(f"inbox       : {config.INBOX_DIR}")
            print(f"summary     : {config.SUMMARY_PATH}")
            print(f"archive     : {config.ARCHIVE_DIR}")
        return 0

    return run()


if __name__ == "__main__":
    sys.exit(main())
