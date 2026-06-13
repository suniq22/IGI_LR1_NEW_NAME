"""
Laboratory Work 3: Python Programming
Task 1 - Series Calculation (e^x)
Version: 3.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This program calculates e^x using Taylor series expansion.
"""

import math
from io_utils import input_float, repeat


def calculate(x, eps):
    """
    Calculates e^x using Taylor series.
    """
    term = 1.0
    result = 1.0
    n = 1

    while abs(term) > eps and n < 500:
        term *= x / n
        result += term
        n += 1

    return result, n


def run():
    """
    Runs Task 1.
    """
    while True:
        print("\n--- Task 1 ---")

        x = input_float("Enter x: ")
        eps = input_float("Enter eps: ")

        if eps <= 0:
            print("Error: eps must be positive")
            continue

        fx, n = calculate(x, eps)

        print(f"x={x} n={n} F(x)={fx} Math={math.exp(x)} eps={eps}")

        if repeat() == 'n':
            break