"""
Module   : drawing.py
Purpose  : Matplotlib drawing of Triangle – fill, axes, text, file export.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from pathlib import Path

from task4.figures import Triangle

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    _MPL = True
except ImportError:
    _MPL = False

_DIR = Path(__file__).parent
FIGURE_FILE = _DIR / "triangle_plot.png"


def draw_triangle(
    triangle: Triangle,
    label: str = "",
    save_path: Path = FIGURE_FILE,
) -> None:
    """
    Draw *triangle* on a matplotlib figure, fill it with its color,
    annotate it with vertex labels and *label* text, then save to *save_path*.

    Parameters
    ----------
    triangle  : Triangle instance to draw.
    label     : Custom text to display inside the figure.
    save_path : Destination PNG path.

    Raises
    ------
    ImportError : If matplotlib is not installed.
    """
    if not _MPL:
        raise ImportError(
            "matplotlib is required for drawing. Run: pip install matplotlib"
        )

    v1, v2, v3 = triangle.vertices()
    xs = [v1[0], v2[0], v3[0], v1[0]]
    ys = [v1[1], v2[1], v3[1], v1[1]]

    fig, ax = plt.subplots(figsize=(8, 6))

    # ── Filled polygon ────────────────────────────────────────────────────
    color = triangle.color
    ax.fill(xs[:3], ys[:3], color=color, alpha=0.4, label=f"Fill: {color}")
    ax.plot(xs, ys, color=color, linewidth=2)

    # ── Vertex labels ─────────────────────────────────────────────────────
    vertex_labels = ["A", "B", "C"]
    offsets = [(-0.05, -0.05), (0.03, -0.05), (0.03, 0.03)]
    for (vx, vy), vl, off in zip([v1, v2, v3], vertex_labels, offsets):
        ax.annotate(
            vl,
            xy=(vx, vy),
            xytext=(vx + off[0] * triangle.a, vy + off[1] * triangle.a),
            fontsize=12, fontweight="bold",
        )

    # ── Side length annotations ───────────────────────────────────────────
    mid_a = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2 - 0.04 * triangle.a)
    mid_c = ((v1[0] + v3[0]) / 2, (v1[1] + v3[1]) / 2)
    mid_b = ((v2[0] + v3[0]) / 2, (v2[1] + v3[1]) / 2)
    ax.text(*mid_a, f"a={triangle.a:.2f}", ha="center", fontsize=9, color="darkblue")
    ax.text(*mid_c, f"c={triangle.side_c():.2f}", ha="center", fontsize=9, color="darkblue")
    ax.text(*mid_b, f"b={triangle.side_b():.2f}", ha="center", fontsize=9, color="darkblue")

    # ── Custom text label inside the triangle ─────────────────────────────
    cx = (v1[0] + v2[0] + v3[0]) / 3
    cy = (v1[1] + v2[1] + v3[1]) / 3
    if label:
        ax.text(
            cx, cy, label,
            ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
        )

    # ── Area annotation ───────────────────────────────────────────────────
    ax.annotate(
        f"Area = {triangle.area():.4f}",
        xy=(cx, cy - 0.1 * triangle.a),
        ha="center", fontsize=10, color="purple",
    )

    # ── Coordinate axes ───────────────────────────────────────────────────
    ax.axhline(0, color="gray", linewidth=0.6, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.6, linestyle="--")

    ax.set_aspect("equal")
    ax.set_title(f"Triangle: {triangle}", fontsize=11)
    ax.legend(handles=[mpatches.Patch(color=color, alpha=0.4, label=f"Color: {color}")])
    ax.grid(True, linestyle=":", alpha=0.4)

    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
