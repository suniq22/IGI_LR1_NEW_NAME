"""
Module   : stats.py
Purpose  : Statistical calculations – mean, median, mode, variance, std dev.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

import math
from typing import List


class Statistics:
    """
    Computes descriptive statistics for a numeric sequence.

    Demonstrates:
    - Dynamic and static class attributes
    - Properties (read-only after construction)
    - Magic methods (__str__, __repr__, __len__, __iter__)
    - Mixin use via StatsMixin
    """

    # Static attribute
    _created: int = 0

    def __init__(self, data: List[float]) -> None:
        """
        Initialise with a numeric sequence.

        Parameters
        ----------
        data : Non-empty list of numbers.

        Raises
        ------
        ValueError : If *data* is empty or contains non-numeric values.
        """
        if not data:
            raise ValueError("Data sequence must not be empty.")
        try:
            self._data = [float(x) for x in data]
        except (TypeError, ValueError):
            raise ValueError("All elements must be numeric.")
        Statistics._created += 1

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def data(self) -> List[float]:
        """The underlying numeric sequence (read-only copy)."""
        return list(self._data)

    @classmethod
    def get_created(cls) -> int:
        """Return the total number of Statistics instances created."""
        return cls._created

    # ── Core statistics ───────────────────────────────────────────────────

    def mean(self) -> float:
        """Return the arithmetic mean of the sequence."""
        return sum(self._data) / len(self._data)

    def median(self) -> float:
        """
        Return the median of the sequence.

        Sorts internally; does not modify the stored data.
        """
        sorted_data = sorted(self._data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 1:
            return sorted_data[mid]
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0

    def mode(self) -> List[float]:
        """
        Return the most frequent value(s) in the sequence.

        Returns
        -------
        list – may contain multiple values if there is a tie.
        """
        freq: dict = {}
        for val in self._data:
            freq[val] = freq.get(val, 0) + 1
        max_freq = max(freq.values())
        return [k for k, v in freq.items() if v == max_freq]

    def variance(self) -> float:
        """Return the population variance of the sequence."""
        m = self.mean()
        return sum((x - m) ** 2 for x in self._data) / len(self._data)

    def std_dev(self) -> float:
        """Return the population standard deviation of the sequence."""
        return math.sqrt(self.variance())

    def summary(self) -> str:
        """Return a formatted summary string of all statistics."""
        return (
            f"N={len(self._data)}  "
            f"mean={self.mean():.4f}  "
            f"median={self.median():.4f}  "
            f"mode={self.mode()}  "
            f"var={self.variance():.4f}  "
            f"std={self.std_dev():.4f}"
        )

    # ── Magic methods ─────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __str__(self) -> str:
        return f"Statistics[n={len(self._data)}]: {self.summary()}"

    def __repr__(self) -> str:
        return f"Statistics(data={self._data!r})"
