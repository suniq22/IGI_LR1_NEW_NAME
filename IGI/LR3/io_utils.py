"""
Laboratory Work 3: Python Programming
Input/Output Module
Version: 1.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This module provides input validation and user interaction utilities.
"""


def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Error: enter integer")


def input_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: enter number")


def input_size():
    while True:
        size = input_int("Enter size: ")
        if size > 0:
            return size
        print("Error: must be positive")


def repeat():
    while True:
        c = input("\nRepeat? (y/n): ").lower()
        if c in ('y', 'n'):
            return c
        print("Error: enter y or n")