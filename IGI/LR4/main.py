"""
Program  : main.py — Laboratory Work 4 Entry Point
Purpose  : Provides a unified menu that runs all five tasks:
             Task 1 – School workload management (CSV + Pickle)
             Task 2 – Text analysis with regular expressions
             Task 3 – e^x series expansion, statistics, matplotlib
             Task 4 – Geometric figures (Triangle), matplotlib drawing
             Task 5 – NumPy array operations and statistics
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16

Usage
-----
Run from the LR4/ directory:
    python main.py
"""

from task1.interface import run_task1
from task2.interface import run_task2
from task3.interface import run_task3
from task4.interface import run_task4
from task5.interface import run_task5

_TASKS = {
    "1": ("School Workload Management (CSV + Pickle)", run_task1),
    "2": ("Text Analysis with Regular Expressions",   run_task2),
    "3": ("e^x Series Expansion + Statistics + Plot", run_task3),
    "4": ("Geometric Figures: Triangle",               run_task4),
    "5": ("NumPy Array Operations and Statistics",     run_task5),
}


def _print_menu() -> None:
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("  LR4 — Object-Oriented Programming in Python")
    print("  Developer: Bryaginya Vladislav  |  Version 1.0")
    print("=" * 60)
    for key, (title, _) in _TASKS.items():
        print(f"  [{key}] {title}")
    print("  [0] Exit")
    print("=" * 60)


def main() -> None:
    """
    Main loop – repeatedly shows the menu and dispatches to the chosen task.

    Provides:
    - Repeat execution without exiting the program
    - Protection against invalid input
    - Specific exception handling per task
    """
    while True:
        _print_menu()
        choice = input("Select a task: ").strip()

        if choice == "0":
            print("\nGoodbye!\n")
            break

        if choice not in _TASKS:
            print(f"  ! '{choice}' is not a valid option. Please choose 0–5.")
            continue

        title, task_fn = _TASKS[choice]
        print(f"\nRunning: {title}")
        try:
            task_fn()
        except KeyboardInterrupt:
            print("\n  (interrupted by user)")
        except Exception as exc:  # noqa: BLE001 — catch-all for safety
            print(f"\n  ! Unexpected error in Task {choice}: {type(exc).__name__}: {exc}")

        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
