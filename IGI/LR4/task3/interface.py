"""
Module   : interface.py
Purpose  : Console interface for Task 3 – series expansion and statistics.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from task3.series import PLOT_FILE, ExpSeries, ExpSeriesRange
from task3.stats import Statistics


def _input_float(prompt: str, lo: float = None, hi: float = None) -> float:
    """Prompt for a float with optional range validation."""
    while True:
        try:
            val = float(input(prompt))
            if lo is not None and val < lo:
                print(f"  ! Value must be ≥ {lo}.")
                continue
            if hi is not None and val > hi:
                print(f"  ! Value must be ≤ {hi}.")
                continue
            return val
        except ValueError:
            print("  ! Please enter a valid number.")


def run_task3() -> None:
    """
    Entry point for Task 3 – e^x series expansion with statistics and plotting.

    Demonstrates:
    - ExpSeries with magic __call__ and __str__
    - ExpSeriesRange with super() and polymorphism
    - Statistics class (mean, median, mode, variance, std)
    - matplotlib plotting (saved to PNG)
    """
    print("\n" + "=" * 60)
    print("  TASK 3 — e^x Series Expansion + Statistics + Plot")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("  [1] Compute e^x for a single value")
        print("  [2] Compute e^x for a range + plot")
        print("  [3] Statistics demo on a custom sequence")
        print("  [0] Return to main menu")
        choice = input("Your choice: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            x = _input_float("  Enter x: ")
            eps = _input_float("  Enter precision ε (e.g. 1e-10): ", lo=0)
            series = ExpSeries(x, eps)
            print(f"\n  {series}")
            val = series()   # __call__
            print(f"  Calling series() → {val:.10f}")

        elif choice == "2":
            print("  Define the x range for the plot.")
            x_start = _input_float("  x start (e.g. -3): ")
            x_end   = _input_float("  x end   (e.g.  3): ")
            if x_end <= x_start:
                print("  ! x end must be greater than x start.")
                continue
            x_step = _input_float("  x step  (e.g.  0.5): ", lo=1e-6)

            sr = ExpSeriesRange(x_start, x_end, x_step)
            rows = sr.compute_range()
            print(f"\n  {sr}")
            sr.print_table(rows)

            try:
                sr.plot(PLOT_FILE)
                print(f"\n  Plot saved to: {PLOT_FILE}")
            except ImportError as exc:
                print(f"\n  ! {exc}")

        elif choice == "3":
            raw = input("  Enter numbers separated by spaces: ")
            try:
                data = [float(v) for v in raw.split()]
                if not data:
                    raise ValueError("Empty input.")
                stats = Statistics(data)
                print(f"\n  {stats}")
                print(f"  Mean     : {stats.mean():.6f}")
                print(f"  Median   : {stats.median():.6f}")
                print(f"  Mode     : {stats.mode()}")
                print(f"  Variance : {stats.variance():.6f}")
                print(f"  Std Dev  : {stats.std_dev():.6f}")
            except ValueError as exc:
                print(f"  ! {exc}")

        else:
            print("  ! Invalid choice.")
