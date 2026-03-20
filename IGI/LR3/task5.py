"""
Laboratory Work 3: Python Programming
Task 5 - List Processing
Version: 3.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This program processes a list of real numbers.
"""

from io_utils import input_float, input_size, repeat
from generator import sequence_generator


def init_manual(size):
    return [input_float(f"Element {i+1}: ") for i in range(size)]


def init_generator(size):
    return list(sequence_generator(size))


def choose_init(size):
    while True:
        print("\n1 - Manual")
        print("2 - Generator")

        c = input("Choose: ")

        if c == '1':
            return init_manual(size)
        elif c == '2':
            return init_generator(size)
        else:
            print("Error")


def find_max_abs(lst):
    return max(lst, key=abs)


def sum_between_positive(lst):
    idx = [i for i, x in enumerate(lst) if x > 0]

    if len(idx) < 2:
        return None

    return sum(lst[idx[0]+1:idx[1]])


def run():
    while True:
        print("\n--- Task 5 ---")

        size = input_size()
        lst = choose_init(size)

        print("List:", lst)
        print("Max abs:", find_max_abs(lst))

        s = sum_between_positive(lst)

        if s is None:
            print("Not enough positives")
        else:
            print("Sum:", s)

        if repeat() == 'n':
            break