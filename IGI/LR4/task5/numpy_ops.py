"""
Module   : numpy_ops.py
Purpose  : NumPy array creation, indexing, operations and statistics.
           Demonstrates array() / values(), indexing, slicing, universal
           functions, mean/median/corrcoef/var/std, plus manual median.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from typing import List, Tuple

try:
    import numpy as np
    _NP = True
except ImportError:
    _NP = False


# ── Mixin ─────────────────────────────────────────────────────────────────────

class PrintMixin:
    """Mixin that provides a formatted matrix printer."""

    def print_matrix(self, matrix, title: str = "Matrix") -> None:
        """
        Pretty-print a 2-D NumPy array.

        Parameters
        ----------
        matrix : 2-D ndarray
        title  : Optional header label
        """
        print(f"\n{title}:")
        print(matrix)


# ── Matrix container ──────────────────────────────────────────────────────────

class IntMatrix(PrintMixin):
    """
    Wraps a random integer NumPy matrix and exposes analysis methods.

    Demonstrates:
    - Static / dynamic class attributes
    - Properties (n, m, data)
    - Magic methods (__str__, __repr__, __getitem__, __len__)
    - Mixin (PrintMixin)
    """

    # Static attribute
    _created: int = 0

    def __init__(self, n: int, m: int, lo: int = -50, hi: int = 50, seed: int = None) -> None:
        """
        Create an n×m random integer matrix.

        Parameters
        ----------
        n    : Number of rows.
        m    : Number of columns.
        lo   : Lower bound for random integers (inclusive).
        hi   : Upper bound for random integers (inclusive).
        seed : Optional RNG seed for reproducibility.

        Raises
        ------
        ImportError : If NumPy is not installed.
        ValueError  : If n or m is not positive.
        """
        if not _NP:
            raise ImportError("NumPy is required. Run: pip install numpy")
        if n <= 0 or m <= 0:
            raise ValueError("Matrix dimensions must be positive integers.")

        rng = np.random.default_rng(seed)
        self._data = rng.integers(lo, hi + 1, size=(n, m))
        self._n = n
        self._m = m
        IntMatrix._created += 1

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def n(self) -> int:
        """Number of rows."""
        return self._n

    @property
    def m(self) -> int:
        """Number of columns."""
        return self._m

    @property
    def data(self):
        """The underlying NumPy ndarray (read-only view)."""
        return self._data.view()

    @classmethod
    def get_created(cls) -> int:
        """Return the total number of IntMatrix instances created."""
        return cls._created

    # ── 1. array() and values() demo ─────────────────────────────────────

    def demo_creation(self) -> None:
        """
        Show array() and an array created from Python values.

        Corresponds to requirement: 'Функции array() и values()'.
        (NumPy has no values() function — we demonstrate creating an array
        from a Python list as the equivalent of 'from values'.)
        """
        print("\n--- 1. Array Creation ---")
        arr_from_list = np.array([10, 20, 30, 40, 50])
        print(f"np.array([...])          : {arr_from_list}")

        arr_zeros  = np.zeros((2, 3), dtype=int)
        arr_ones   = np.ones((2, 3),  dtype=int)
        arr_eye    = np.eye(3,         dtype=int)
        arr_range  = np.arange(1, 11)
        arr_linsp  = np.linspace(0, 1, 5)
        arr_full   = np.full((2, 4), fill_value=7)

        print(f"np.zeros((2,3))          :\n{arr_zeros}")
        print(f"np.ones((2,3))           :\n{arr_ones}")
        print(f"np.eye(3)                :\n{arr_eye}")
        print(f"np.arange(1,11)          : {arr_range}")
        print(f"np.linspace(0,1,5)       : {arr_linsp}")
        print(f"np.full((2,4),7)         :\n{arr_full}")

    # ── 2. Indexing and slicing ───────────────────────────────────────────

    def demo_indexing(self) -> None:
        """
        Show element access, row/column slices, and fancy indexing.

        Corresponds to requirement: 'Индексирование. Индекс и срез.'
        """
        print("\n--- 2. Indexing and Slicing ---")
        self.print_matrix(self._data, f"Original {self._n}×{self._m} matrix")
        print(f"Element [0,0]      : {self._data[0, 0]}")
        print(f"First row          : {self._data[0, :]}")
        print(f"Last  row          : {self._data[-1, :]}")
        print(f"First column       : {self._data[:, 0]}")
        print(f"Sub-matrix [0:2, 0:2]:\n{self._data[0:2, 0:2]}")
        # Fancy indexing – elements where value > 0
        positive_mask = self._data > 0
        print(f"Positive elements  : {self._data[positive_mask]}")

    # ── 3. Universal (element-wise) operations ────────────────────────────

    def demo_operations(self) -> None:
        """
        Show arithmetic and universal NumPy functions applied element-wise.

        Corresponds to requirement: 'Операции. Универсальные функции.'
        """
        print("\n--- 3. Array Operations (Universal Functions) ---")
        print(f"Original last row  : {self._data[-1, :]}")
        print(f"abs(last row)      : {np.abs(self._data[-1, :])}")
        print(f"sqrt(abs(last row)): {np.sqrt(np.abs(self._data[-1, :].astype(float)))}")
        print(f"matrix + 10        :\n{self._data + 10}")
        print(f"matrix * 2         :\n{self._data * 2}")

    # ── 4. Statistical operations ─────────────────────────────────────────

    def stats_full_matrix(self) -> dict:
        """
        Compute mean, median, corrcoef, var, std for the entire matrix.

        Returns
        -------
        dict with keys: mean, median, corrcoef, var, std
        """
        flat = self._data.flatten().astype(float)
        return {
            "mean":    np.mean(flat),
            "median":  np.median(flat),
            "corrcoef": np.corrcoef(self._data.astype(float)),  # row-wise correlation
            "var":     np.var(flat),
            "std":     np.std(flat),
        }

    def demo_stats(self) -> None:
        """
        Print mean, median, corrcoef, var, std for the matrix.

        Corresponds to requirement: 'Математические и статистические операции'.
        """
        print("\n--- 4. Mathematical & Statistical Operations ---")
        s = self.stats_full_matrix()
        print(f"mean()    : {s['mean']:.4f}")
        print(f"median()  : {s['median']:.4f}")
        print(f"var()     : {s['var']:.4f}")
        print(f"std()     : {s['std']:.4f}")
        print(f"corrcoef():\n{s['corrcoef']}")

    # ── 5. Sort last row + median (two ways) ─────────────────────────────

    def sort_last_row(self) -> None:
        """Sort the last row of the matrix in ascending order (in-place)."""
        self._data[-1, :] = np.sort(self._data[-1, :])

    def median_last_row_numpy(self) -> float:
        """
        Compute the median of the (sorted) last row using np.median().

        Returns
        -------
        float
        """
        return float(np.median(self._data[-1, :]))

    def median_last_row_manual(self) -> float:
        """
        Compute the median of the last row using the manual formula.

        Formula:
            sorted_arr = sorted(last_row)
            if n is odd  → median = arr[n//2]
            if n is even → median = (arr[n//2 - 1] + arr[n//2]) / 2

        Returns
        -------
        float
        """
        row = sorted(self._data[-1, :].tolist())
        n = len(row)
        if n % 2 == 1:
            return float(row[n // 2])
        return (row[n // 2 - 1] + row[n // 2]) / 2.0

    def demo_last_row(self) -> None:
        """
        Sort last row, then compute its median both ways and compare.

        Corresponds to requirements:
        'Отсортировать по возрастанию элементы последней строки.'
        'Вычислить медиану двумя способами.'
        """
        print("\n--- 5. Last Row: Sort + Median ---")
        print(f"Last row (before sort): {self._data[-1, :]}")
        self.sort_last_row()
        print(f"Last row (after sort) : {self._data[-1, :]}")

        med_np  = self.median_last_row_numpy()
        med_man = self.median_last_row_manual()
        print(f"\nMedian (np.median)    : {med_np:.4f}")
        print(f"Median (manual)       : {med_man:.4f}")
        match = "✓ Match" if abs(med_np - med_man) < 1e-9 else "✗ Mismatch"
        print(f"Comparison            : {match}")

    # ── Magic methods ─────────────────────────────────────────────────────

    def __len__(self) -> int:
        return self._n * self._m

    def __getitem__(self, idx):
        return self._data[idx]

    def __str__(self) -> str:
        return f"IntMatrix({self._n}×{self._m}):\n{self._data}"

    def __repr__(self) -> str:
        return f"IntMatrix(n={self._n}, m={self._m})"
