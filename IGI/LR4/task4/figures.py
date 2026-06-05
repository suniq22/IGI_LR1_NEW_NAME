"""
Module   : figures.py
Purpose  : Abstract geometric figure classes and Triangle implementation.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple


# ── Mixin ─────────────────────────────────────────────────────────────────────

class DescriptionMixin:
    """Mixin that adds a verbose description helper."""

    def describe(self) -> str:
        """Return a human-readable description of the figure."""
        raise NotImplementedError("Subclasses must implement describe().")


# ── Color class ───────────────────────────────────────────────────────────────

class FigureColor:
    """
    Encapsulates the color of a geometric figure.

    Demonstrates:
    - Property with getter and setter
    - __str__ / __repr__ magic methods
    """

    KNOWN_COLORS = {
        "red", "green", "blue", "yellow", "orange",
        "purple", "pink", "brown", "black", "white", "gray",
    }

    def __init__(self, color: str) -> None:
        """
        Parameters
        ----------
        color : Color name (case-insensitive).
        """
        self.color = color   # uses property setter

    @property
    def color(self) -> str:
        """The color name (lowercase)."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Color must be a non-empty string.")
        self._color = value.strip().lower()

    def is_known(self) -> bool:
        """Return True if this color is in the known set."""
        return self._color in self.KNOWN_COLORS

    def __str__(self) -> str:
        return self._color

    def __repr__(self) -> str:
        return f"FigureColor(color={self._color!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FigureColor):
            return self._color == other._color
        if isinstance(other, str):
            return self._color == other.lower()
        return NotImplemented


# ── Abstract base ─────────────────────────────────────────────────────────────

class GeometricFigure(ABC, DescriptionMixin):
    """
    Abstract base class for all geometric figures.

    Requires subclasses to implement area().

    Demonstrates:
    - Abstract method (abc.abstractmethod)
    - Static figure_name field
    - Class method returning the figure name
    - Magic methods (__str__, __repr__)
    """

    # Dynamic class attribute – will be overridden per subclass
    figure_name: str = "GeometricFigure"

    def __init__(self, color: str) -> None:
        """
        Parameters
        ----------
        color : Color name for the figure.
        """
        self._color_obj = FigureColor(color)   # composition: FigureColor instance

    # ── Color property ────────────────────────────────────────────────────

    @property
    def color(self) -> str:
        """Figure color as a string."""
        return str(self._color_obj)

    @color.setter
    def color(self, value: str) -> None:
        self._color_obj.color = value

    # ── Abstract method ───────────────────────────────────────────────────

    @abstractmethod
    def area(self) -> float:
        """Compute and return the area of the figure."""

    # ── Class method ──────────────────────────────────────────────────────

    @classmethod
    def get_name(cls) -> str:
        """Return the figure type name."""
        return cls.figure_name

    # ── Magic methods ─────────────────────────────────────────────────────

    def __str__(self) -> str:
        return f"{self.figure_name} | color={self.color} | area={self.area():.4f}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(color={self.color!r})"

    def describe(self) -> str:
        return self.__str__()


# ── Triangle ──────────────────────────────────────────────────────────────────

class Triangle(GeometricFigure):
    """
    Triangle defined by side *a* and the two angles *B* and *C* adjacent to it.

    The triangle is built using the law of sines:
        A = 180° − B − C
        b = a · sin(B) / sin(A)
        c = a · sin(C) / sin(A)
        area = 0.5 · b · c · sin(A)

    Demonstrates:
    - super() in __init__
    - Properties for a, angle_B, angle_C
    - Overriding area() (polymorphism)
    - format() in __str__
    - Class-level figure_name
    """

    figure_name: str = "Triangle"

    def __init__(self, a: float, angle_B: float, angle_C: float, color: str = "blue") -> None:
        """
        Parameters
        ----------
        a       : Length of side a.
        angle_B : Angle B (degrees), adjacent to side a.
        angle_C : Angle C (degrees), adjacent to side a.
        color   : Fill color (default 'blue').

        Raises
        ------
        ValueError : If geometry is invalid.
        """
        super().__init__(color)    # super() call → GeometricFigure.__init__
        self.a = a
        self.angle_B = angle_B
        self.angle_C = angle_C
        self._validate_geometry()

    def _validate_geometry(self) -> None:
        """Raise ValueError if the angles are geometrically impossible."""
        if self._angle_A() <= 0:
            raise ValueError(
                f"Angles B={self._angle_B}° and C={self._angle_C}° "
                f"leave A={self._angle_A():.2f}° ≤ 0 — invalid triangle."
            )

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def a(self) -> float:
        """Side a."""
        return self._a

    @a.setter
    def a(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Side a must be a positive number.")
        if value <= 0:
            raise ValueError("Side a must be positive.")
        self._a = value

    @property
    def angle_B(self) -> float:
        """Angle B in degrees."""
        return self._angle_B

    @angle_B.setter
    def angle_B(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Angle B must be a number in (0, 180).")
        if not (0 < value < 180):
            raise ValueError("Angle B must be in (0°, 180°).")
        self._angle_B = value

    @property
    def angle_C(self) -> float:
        """Angle C in degrees."""
        return self._angle_C

    @angle_C.setter
    def angle_C(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Angle C must be a number in (0, 180).")
        if not (0 < value < 180):
            raise ValueError("Angle C must be in (0°, 180°).")
        self._angle_C = value

    # ── Derived geometry ──────────────────────────────────────────────────

    def _angle_A(self) -> float:
        """Compute angle A = 180 − B − C (degrees)."""
        return 180.0 - self._angle_B - self._angle_C

    def side_b(self) -> float:
        """Compute side b via the law of sines."""
        A_rad = math.radians(self._angle_A())
        B_rad = math.radians(self._angle_B)
        return self._a * math.sin(B_rad) / math.sin(A_rad)

    def side_c(self) -> float:
        """Compute side c via the law of sines."""
        A_rad = math.radians(self._angle_A())
        C_rad = math.radians(self._angle_C)
        return self._a * math.sin(C_rad) / math.sin(A_rad)

    def vertices(self) -> Tuple[Tuple[float, float], ...]:
        """
        Return the three vertices of the triangle as (x, y) tuples.

        Vertex 1 is at the origin, vertex 2 at (a, 0).
        Vertex 3 is located via the angles B (at V1) and C (at V2).

        Returns
        -------
        ((x1, y1), (x2, y2), (x3, y3))
        """
        B_rad = math.radians(self._angle_B)
        C_rad = math.radians(self._angle_C)
        x1, y1 = 0.0, 0.0
        x2, y2 = self._a, 0.0
        # Solve for third vertex intersection
        # Line from V1 at angle B: x = t*cos(B), y = t*sin(B)
        # Line from V2 at angle (180-C): x = a - s*cos(C), y = s*sin(C)
        # => t = a * sin(C) / sin(B+C)
        BpC = B_rad + C_rad
        t = self._a * math.sin(C_rad) / math.sin(BpC)
        x3 = t * math.cos(B_rad)
        y3 = t * math.sin(B_rad)
        return (x1, y1), (x2, y2), (x3, y3)

    # ── Abstract method implementation ────────────────────────────────────

    def area(self) -> float:
        """
        Return the area of the triangle.

        Area = 0.5 · b · c · sin(A)
        """
        A_rad = math.radians(self._angle_A())
        return 0.5 * self.side_b() * self.side_c() * math.sin(A_rad)

    # ── String representation using format() ─────────────────────────────

    def describe(self) -> str:
        """Return a detailed human-readable description using str.format()."""
        return (
            "Figure   : {name}\n"
            "Color    : {color}\n"
            "Side a   : {a:.4f}\n"
            "Angle B  : {B:.2f}°\n"
            "Angle C  : {C:.2f}°\n"
            "Angle A  : {A:.2f}°\n"
            "Side b   : {b:.4f}\n"
            "Side c   : {c:.4f}\n"
            "Area     : {area:.4f}"
        ).format(
            name=self.figure_name,
            color=self.color,
            a=self._a,
            B=self._angle_B,
            C=self._angle_C,
            A=self._angle_A(),
            b=self.side_b(),
            c=self.side_c(),
            area=self.area(),
        )

    def __str__(self) -> str:
        return (
            "{name} [color={color}]: a={a:.4f}, B={B:.1f}°, "
            "C={C:.1f}°, area={area:.4f}"
        ).format(
            name=self.figure_name,
            color=self.color,
            a=self._a,
            B=self._angle_B,
            C=self._angle_C,
            area=self.area(),
        )

    def __repr__(self) -> str:
        return (
            f"Triangle(a={self._a!r}, angle_B={self._angle_B!r}, "
            f"angle_C={self._angle_C!r}, color={self.color!r})"
        )
