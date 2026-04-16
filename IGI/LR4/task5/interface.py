"""
Module   : interface.py
Purpose  : Console interface for Task 5 – NumPy operations.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from task5.numpy_ops import IntMatrix


def _input_int(prompt: str, lo: int = 1) -> int:
    """Prompt for a positive integer."""
    while True:
        try:
            val = int(input(prompt))
            if val < lo:
                print(f"  ! Value must be ≥ {lo}.")
                continue
            return val
        except ValueError:
            print("  ! Please enter a valid integer.")


def run_task5() -> None:
    """
    Entry point for Task 5 – NumPy array operations.

    Demonstrates:
    - np.array(), zeros, ones, eye, arange, linspace, full
    - Indexing, slicing, fancy indexing
    - Universal (element-wise) operations
    - mean(), median(), corrcoef(), var(), std()
    - Sorting last row, median via numpy and manual formula
    - Properties, magic methods, PrintMixin
    """
    print("\n" + "=" * 60)
    print("  TASK 5 — NumPy Array Operations and Statistics")
    print("=" * 60)

    try:
        import numpy  # noqa: F401
    except ImportError:
        print("  ! NumPy is not installed. Run: pip install numpy")
        return

    while True:
        print("\nOptions:")
        print("  [1] Run full NumPy demo with a random matrix")
        print("  [0] Return to main menu")
        choice = input("Your choice: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            n = _input_int("  Number of rows    n (≥ 2): ", lo=2)
            m = _input_int("  Number of columns m (≥ 2): ", lo=2)
            seed_raw = input("  Random seed (press Enter for random): ").strip()
            seed = int(seed_raw) if seed_raw.lstrip("-").isdigit() else None

            try:
                mat = IntMatrix(n, m, seed=seed)
            except (ImportError, ValueError) as exc:
                print(f"  ! {exc}")
                continue

            print(f"\n  {repr(mat)}")
            print(f"  len(mat) = {len(mat)}")
            print(f"  mat[0,0] = {mat[0, 0]}")

            mat.demo_creation()
            mat.demo_indexing()
            mat.demo_operations()
            mat.demo_stats()
            mat.demo_last_row()

            print(f"\n  Total IntMatrix instances: {IntMatrix.get_created()}")

        else:
            print("  ! Invalid choice.")
