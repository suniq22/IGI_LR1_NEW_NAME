"""
Module   : interface.py
Purpose  : Console interface for Task 2 – text analysis.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from pathlib import Path

from task2.analyzer import (
    MACFocusedAnalyzer,
    TextAnalyzer,
    archive_result,
    print_archive_info,
)

_DIR = Path(__file__).parent
DEFAULT_INPUT  = _DIR / "sample_text.txt"
RESULT_FILE    = _DIR / "analysis_result.txt"
ARCHIVE_FILE   = _DIR / "analysis_result.zip"


def run_task2() -> None:
    """
    Entry point for Task 2 – text analysis with regular expressions.

    Demonstrates:
    - Regex-based sentence/word/smiley/MAC analysis
    - Polymorphism (MACFocusedAnalyzer extends TextAnalyzer)
    - super() inside MACFocusedAnalyzer
    - Mixins (LogMixin, SaveMixin)
    - ZIP archiving with zipfile
    """
    print("\n" + "=" * 60)
    print("  TASK 2 — Text Analysis with Regular Expressions")
    print("=" * 60)

    # ── Choose source ──────────────────────────────────────────────────────
    print(f"\nDefault text file: {DEFAULT_INPUT}")
    custom = input("Enter a different file path (or press Enter to use default): ").strip()
    source = Path(custom) if custom else DEFAULT_INPUT

    try:
        analyzer = MACFocusedAnalyzer.from_file(source)
        analyzer.log(f"Loaded {len(analyzer)} characters from '{source.name}'.")
    except FileNotFoundError as exc:
        print(f"  ! {exc}")
        return
    except ValueError as exc:
        print(f"  ! {exc}")
        return

    # ── Full report ────────────────────────────────────────────────────────
    report = analyzer.full_report()
    print(report)

    # ── Save report ────────────────────────────────────────────────────────
    analyzer.save_to_file(RESULT_FILE, report)
    print(f"\nReport saved to: {RESULT_FILE}")

    # ── Archive ────────────────────────────────────────────────────────────
    archive_result(RESULT_FILE, ARCHIVE_FILE)
    print_archive_info(ARCHIVE_FILE)

    # ── Interactive MAC validation ─────────────────────────────────────────
    print()
    while True:
        addr = input(
            "Enter a string to validate as MAC address (or press Enter to skip): "
        ).strip()
        if not addr:
            break
        valid = TextAnalyzer.is_valid_mac(addr)
        status = "VALID" if valid else "INVALID"
        print(f"  '{addr}' → {status}")
        again = input("Validate another? [y/n]: ").strip().lower()
        if again != "y":
            break

    print(f"\nTotal TextAnalyzer instances created: {TextAnalyzer.get_instance_count()}")
