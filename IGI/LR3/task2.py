"""
Laboratory Work 3: Python Programming
Task 2 - Sequence Analysis
Version: 3.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This program counts non-negative numbers in a sequence.
"""

from io_utils import input_int, repeat
from generator import sequence_generator


def init_manual():
    """
    Manual input until number < -100.
    """
    seq = []

    while True:
        x = input_int("Enter number: ")
        if x < -100:
            break
        seq.append(x)

    return seq


def init_generator():
    """
    Generator-based initialization.
    """
    seq = []

    for x in sequence_generator(200):
        if x < -100:
            break
        seq.append(int(x))

    return seq


def choose_init():
    while True:
        print("\n1 - Manual")
        print("2 - Generator")

        c = input("Choose: ")

        if c == '1':
            return init_manual()
        elif c == '2':
            return init_generator()
        else:
            print("Error")


def count_non_negative(seq):
    return sum(1 for x in seq if x >= 0)


def run():
    while True:
        print("\n--- Task 2 ---")

        seq = choose_init()

        print("Sequence:", seq)
        print("Count:", count_non_negative(seq))

        if repeat() == 'n':
            break