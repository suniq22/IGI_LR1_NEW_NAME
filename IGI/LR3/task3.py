"""
Laboratory Work 3: Python Programming
Task 3 - Text Analysis (without regex)
Version: 3.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This program counts words starting with lowercase letters.
"""

from io_utils import repeat


def clean(word):
    return word.strip(".,!?;:\"()")


def count_lowercase(text):
    words = text.split()
    count = 0

    for w in words:
        w = clean(w)
        if w and w[0].islower():
            count += 1

    return count


def run():
    while True:
        print("\n--- Task 3 ---")

        text = input("Enter text: ")

        print("Count:", count_lowercase(text))

        if repeat() == 'n':
            break