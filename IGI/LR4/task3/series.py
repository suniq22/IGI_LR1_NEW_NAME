"""
Module   : series.py
Purpose  : e^x Maclaurin series expansion, matplotlib plotting, file export.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

import math
from pathlib import Path
from typing import List, Tuple

from task3.stats import Statistics

# matplotlib is an optional dependency; we guard the import
try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend (safe in all envs)
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False

_DIR = Path(__file__).parent
PLOT_FILE = _DIR / "exp_series_plot.png"


# ── Mixin ─────────────────────────────────────────────────────────────────────

class TableMixin:
    """Mixin that provides a formatted table printer for (x, F, n, Math) data."""

    def print_table(self, rows: List[Tuple]) -> None:
        """
        Print tabular results.

        Parameters
        ----------
        rows : list of (x, series_value, terms_used, math_value)
        """
        header = f"{'x':>8} {'F(x) series':>14} {'n':>5} {'Math F(x)':>14} {'Error':>12}"
        print(header)
        print("-" * len(header))
        for x, fx_series, n, fx_math in rows:
            error = abs(fx_series - fx_math)
            print(f"{x:>8.4f} {fx_series:>14.8f} {n:>5} {fx_math:>14.8f} {error:>12.2e}")


# ── Series expansion ──────────────────────────────────────────────────────────

class ExpSeries(TableMixin):
    """
    Computes the Maclaurin series for e^x: Σ x^n / n!

    Demonstrates:
    - Static/dynamic class attributes
    - Properties (x, precision)
    - Magic methods (__str__, __repr__, __call__)
    - super() (used in subclass)
    - Mixin (TableMixin)
    """

    # Static attribute – default precision threshold
    DEFAULT_EPS: float = 1e-10

    def __init__(self, x: float, eps: float = DEFAULT_EPS) -> None:
        """
        Initialise for a given argument *x*.

        Parameters
        ----------
        x   : The argument of e^x.
        eps : Convergence threshold (stop when |term| < eps).
        """
        self.x = x     # uses property setter
        self.eps = eps  # uses property setter

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def x(self) -> float:
        """The argument x."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        try:
            self._x = float(value)
        except (TypeError, ValueError):
            raise ValueError("x must be a real number.")

    @property
    def eps(self) -> float:
        """Convergence threshold ε."""
        return self._eps

    @eps.setter
    def eps(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("eps must be a real number.")
        if value <= 0:
            raise ValueError("eps must be positive.")
        self._eps = value

    # ── Computation ───────────────────────────────────────────────────────

    def compute(self) -> Tuple[float, int]:
        """
        Evaluate e^x via Maclaurin series.

        Returns
        -------
        (series_value, number_of_terms_used)
        """
        total = 0.0
        term = 1.0    # x^0 / 0! = 1
        n = 0
        while abs(term) >= self._eps:
            total += term
            n += 1
            term *= self._x / n
        return total, n

    def math_value(self) -> float:
        """Return math.exp(x) for comparison."""
        return math.exp(self._x)

    def __call__(self) -> float:
        """Calling the object computes and returns the series value."""
        return self.compute()[0]

    def __str__(self) -> str:
        val, n = self.compute()
        return (
            f"ExpSeries(x={self._x}, ε={self._eps}) → "
            f"series={val:.8f}, math={self.math_value():.8f}, terms={n}"
        )

    def __repr__(self) -> str:
        return f"ExpSeries(x={self._x!r}, eps={self._eps!r})"


class ExpSeriesRange(ExpSeries):
    """
    Computes e^x series for a range of x values and plots results.

    Demonstrates super() and polymorphism.
    """

    def __init__(
        self,
        x_start: float,
        x_end: float,
        x_step: float,
        eps: float = ExpSeries.DEFAULT_EPS,
    ) -> None:
        """
        Initialise for a range [x_start, x_end] with step x_step.

        Parameters
        ----------
        x_start : Left boundary.
        x_end   : Right boundary.
        x_step  : Step between x values.
        eps     : Convergence threshold.
        """
        super().__init__(x_start, eps)   # super() call
        self._x_start = x_start
        self._x_end = x_end
        self._x_step = x_step

    def _x_values(self) -> List[float]:
        """Generate the list of x values in the range."""
        values = []
        x = self._x_start
        while x <= self._x_end + 1e-12:
            values.append(round(x, 10))
            x += self._x_step
        return values

    def compute_range(self) -> List[Tuple[float, float, int, float]]:
        """
        Compute series for every x in the range.

        Returns
        -------
        list of (x, series_value, n_terms, math_value)
        """
        results = []
        for xv in self._x_values():
            self.x = xv          # reuse property setter
            val, n = self.compute()
            results.append((xv, val, n, self.math_value()))
        return results

    def plot(self, save_path: Path = PLOT_FILE) -> None:
        """
        Plot both the series approximation and math.exp on one axes.

        Saves the figure to *save_path*.

        Parameters
        ----------
        save_path : Destination PNG path.

        Raises
        ------
        ImportError : If matplotlib is not installed.
        """
        if not _MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for plotting. Run: pip install matplotlib")

        rows = self.compute_range()
        xs          = [r[0] for r in rows]
        ys_series   = [r[1] for r in rows]
        ys_math     = [r[3] for r in rows]

        # Compute statistics on series values
        stats = Statistics(ys_series)

        fig, ax = plt.subplots(figsize=(10, 6))

        # ── Plot both curves ───────────────────────────────────────────
        ax.plot(xs, ys_series, color="royalblue", linewidth=2,
                linestyle="--", marker="o", markersize=4, label="Series e^x")
        ax.plot(xs, ys_math,   color="tomato",    linewidth=2,
                linestyle="-",  label="math.exp(x)")

        # ── Coordinate axes through origin ────────────────────────────
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)

        # ── Annotation: mark the point at x=1 ────────────────────────
        if min(xs) <= 1.0 <= max(xs):
            y_at_1 = math.exp(1.0)
            ax.annotate(
                f"e¹ ≈ {y_at_1:.4f}",
                xy=(1.0, y_at_1),
                xytext=(1.2, y_at_1 * 0.8),
                arrowprops=dict(arrowstyle="->", color="green"),
                fontsize=10,
                color="green",
            )

        # ── Text box with statistics ──────────────────────────────────
        stats_text = (
            f"μ = {stats.mean():.4f}\n"
            f"σ = {stats.std_dev():.4f}\n"
            f"med = {stats.median():.4f}"
        )
        ax.text(
            0.02, 0.97, stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        ax.set_title("e^x — Maclaurin Series vs math.exp(x)", fontsize=14)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.5)

        fig.tight_layout()
        fig.savefig(save_path, dpi=150)
        plt.close(fig)

    def __str__(self) -> str:
        return (
            f"ExpSeriesRange(x=[{self._x_start}, {self._x_end}], "
            f"step={self._x_step}, ε={self._eps})"
        )
