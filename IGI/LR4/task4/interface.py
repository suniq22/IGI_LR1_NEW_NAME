"""
Module   : interface.py
Purpose  : Console interface for Task 4 – geometric figures.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from task4.drawing import FIGURE_FILE, draw_triangle
from task4.figures import FigureColor, GeometricFigure, Triangle


def _input_float(prompt: str, lo: float = None) -> float:
    """Prompt the user for a float, optionally checking a lower bound."""
    while True:
        try:
            val = float(input(prompt))
            if lo is not None and val <= lo:
                print(f"  ! Value must be > {lo}.")
                continue
            return val
        except ValueError:
            print("  ! Please enter a valid number.")


def _input_color(prompt: str = "  Fill color (e.g. blue): ") -> str:
    """Prompt for a color string; warn but allow unknown colors."""
    while True:
        color = input(prompt).strip()
        if color:
            fc = FigureColor.__new__(FigureColor)
            fc._color = color.lower()
            if not fc.is_known():
                confirm = input(
                    f"  '{color}' is not a standard color. Use it anyway? [y/n]: "
                ).strip().lower()
                if confirm != "y":
                    continue
            return color
        print("  ! Color cannot be empty.")


def run_task4() -> None:
    """
    Entry point for Task 4 – Triangle class with drawing.

    Demonstrates:
    - Abstract base class (GeometricFigure)
    - FigureColor composition
    - Triangle: super(), properties, area(), describe(), format()
    - DescriptionMixin
    - matplotlib drawing (filled, labeled, saved to PNG)
    - Polymorphism: get_name() class method
    """
    print("\n" + "=" * 60)
    print("  TASK 4 — Geometric Figures: Triangle")
    print("=" * 60)

    print(f"\nFigure type: {Triangle.get_name()}")

    while True:
        print("\nOptions:")
        print("  [1] Build triangle with default example (a=5, B=60°, C=70°, blue)")
        print("  [2] Enter triangle parameters manually")
        print("  [0] Return to main menu")
        choice = input("Your choice: ").strip()

        if choice == "0":
            break

        elif choice in ("1", "2"):
            if choice == "1":
                a, B, C, color = 5.0, 60.0, 70.0, "blue"
            else:
                a     = _input_float("  Side a (> 0): ", lo=0)
                B     = _input_float("  Angle B in degrees (0 < B < 180): ", lo=0)
                C     = _input_float("  Angle C in degrees (0 < C < 180): ", lo=0)
                color = _input_color()

            try:
                tri = Triangle(a, B, C, color)
            except ValueError as exc:
                print(f"  ! Cannot create triangle: {exc}")
                continue

            print(f"\n  repr: {repr(tri)}")
            print(f"  str : {tri}")
            print(f"\n  Detailed description:\n")
            print(tri.describe())
            print(f"\n  Vertices: {tri.vertices()}")

            # Custom label text
            label = input("\n  Enter text to display inside the triangle figure: ").strip()

            try:
                draw_triangle(tri, label=label, save_path=FIGURE_FILE)
                print(f"\n  Figure saved to: {FIGURE_FILE}")
            except ImportError as exc:
                print(f"  ! {exc}")

            # Demonstrate polymorphism via base class reference
            fig_ref: GeometricFigure = tri
            print(f"\n  Via base ref — area()  : {fig_ref.area():.4f}")
            print(f"  Via base ref — color   : {fig_ref.color}")
            print(f"  Via base ref — get_name: {fig_ref.get_name()}")

            # FigureColor demo
            fc = FigureColor(color)
            print(f"\n  FigureColor repr: {repr(fc)}")
            print(f"  FigureColor str : {fc}")
            print(f"  Is known color? : {fc.is_known()}")

        else:
            print("  ! Invalid choice.")
