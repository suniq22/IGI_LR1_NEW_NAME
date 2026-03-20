"""
Laboratory Work 3: Python Programming
Task 4 - Static Text Analysis
Version: 3.0
Developer: Bryginya Vladislav Vasilevich
Date: 19.03.2026

This program analyzes a predefined text string.
"""

from io_utils import repeat

TEXT = """So she was considering in her own mind, as well as she could, for the hot day made her feel very sleepy and stupid, whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her."""


def clean(word):
    return word.strip(".,!?;:\"()").lower()


def count_min(words):
    cleaned = [clean(w) for w in words if clean(w)]
    m = min(len(w) for w in cleaned)
    return sum(1 for w in cleaned if len(w) == m)


def words_before_comma(words):
    return [w[:-1] for w in words if w.endswith(',')]


def longest_y(words):
    cleaned = [clean(w) for w in words]
    candidates = [w for w in cleaned if w.endswith('y')]

    if not candidates:
        return None

    return max(candidates, key=len)


def run():
    while True:
        print("\n--- Task 4 ---")

        words = TEXT.split()

        print("a:", count_min(words))
        print("b:", words_before_comma(words))
        print("c:", longest_y(words))

        if repeat() == 'n':
            break