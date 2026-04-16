"""
Module   : models.py
Purpose  : Data models for the school workload management system.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from __future__ import annotations
from typing import Any


# ── Mixins ────────────────────────────────────────────────────────────────────

class SerializableMixin:
    """Mixin that adds dictionary serialization to any class."""

    def to_dict(self) -> dict:
        """Return a plain-dict representation of this object."""
        raise NotImplementedError("Subclasses must implement to_dict().")

    @classmethod
    def from_dict(cls, data: dict) -> Any:
        """Reconstruct an instance from a plain dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict().")


class ReprMixin:
    """Mixin that auto-generates __repr__ from instance __dict__."""

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        attrs = ", ".join(
            f"{k.lstrip('_')}={v!r}" for k, v in vars(self).items()
        )
        return f"{self.__class__.__name__}({attrs})"


# ── Main model ────────────────────────────────────────────────────────────────

class WorkloadRecord(SerializableMixin, ReprMixin):
    """
    Represents one teacher-workload entry (teacher, class, hours).

    Class attributes
    ----------------
    _total_records : int
        Static counter incremented on every instantiation.

    Instance attributes
    -------------------
    teacher    : str  – Teacher's last name.
    class_name : str  – Class identifier, e.g. '10A'.
    hours      : int  – Weekly teaching hours (positive integer).
    """

    # Static (class-level) attribute
    _total_records: int = 0

    def __init__(self, teacher: str, class_name: str, hours: int) -> None:
        """
        Initialise a WorkloadRecord.

        Parameters
        ----------
        teacher    : Teacher's last name.
        class_name : Class identifier.
        hours      : Positive integer teaching hours.

        Raises
        ------
        ValueError : If any argument fails validation.
        """
        self.teacher = teacher        # routed through property setter
        self.class_name = class_name
        self.hours = hours
        WorkloadRecord._total_records += 1

    # ── Properties (getters + setters) ────────────────────────────────────

    @property
    def teacher(self) -> str:
        """Teacher's last name."""
        return self._teacher

    @teacher.setter
    def teacher(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Teacher name must be a non-empty string.")
        self._teacher = value.strip()

    @property
    def class_name(self) -> str:
        """Class identifier."""
        return self._class_name

    @class_name.setter
    def class_name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Class name must be a non-empty string.")
        self._class_name = value.strip()

    @property
    def hours(self) -> int:
        """Weekly teaching hours."""
        return self._hours

    @hours.setter
    def hours(self, value: int) -> None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Hours must be convertible to a positive integer.")
        if value <= 0:
            raise ValueError("Hours must be a positive integer.")
        self._hours = value

    # ── Class-level helpers ────────────────────────────────────────────────

    @classmethod
    def get_total_records(cls) -> int:
        """Return the total number of WorkloadRecord instances created."""
        return cls._total_records

    # ── Serialisation ──────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a plain dictionary for CSV / JSON serialisation."""
        return {
            "teacher": self._teacher,
            "class_name": self._class_name,
            "hours": self._hours,
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorkloadRecord:
        """Reconstruct a WorkloadRecord from a plain dictionary."""
        return cls(data["teacher"], data["class_name"], int(data["hours"]))

    # ── Magic methods ──────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"{self._teacher:<20} | "
            f"Class: {self._class_name:<6} | "
            f"Hours: {self._hours:>4}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkloadRecord):
            return NotImplemented
        return (
            self._teacher == other._teacher
            and self._class_name == other._class_name
            and self._hours == other._hours
        )

    def __lt__(self, other: WorkloadRecord) -> bool:
        if not isinstance(other, WorkloadRecord):
            return NotImplemented
        return self._hours < other._hours

    def __add__(self, other: WorkloadRecord) -> int:
        """Support sum() – returns combined hours."""
        if isinstance(other, WorkloadRecord):
            return self._hours + other._hours
        if isinstance(other, int):
            return self._hours + other
        return NotImplemented

    def __radd__(self, other: int) -> int:
        """Right-add so that sum(records, 0) works."""
        return self._hours + other
