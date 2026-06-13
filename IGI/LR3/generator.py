"""
Laboratory Work 3: Python Programming
Generator Module
Version: 1.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This module contains generator functions using yield.
"""


def sequence_generator(size):
    """
    Generator that yields float values from 0 to size-1.
    """
    for i in range(size):
        yield float(i)