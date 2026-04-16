"""
Module   : analysis.py
Purpose  : Workload analysis functions – aggregation, min/max, lookup.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from typing import Dict, List, Optional, Tuple

from task1.models import WorkloadRecord


def compute_workload(records: List[WorkloadRecord]) -> Dict[str, int]:
    """
    Aggregate total teaching hours per teacher.

    Parameters
    ----------
    records : list of WorkloadRecord

    Returns
    -------
    dict mapping teacher name → total hours
    """
    result: Dict[str, int] = {}
    for rec in records:
        result[rec.teacher] = result.get(rec.teacher, 0) + rec.hours
    return result


def get_max_teacher(workload: Dict[str, int]) -> Tuple[str, int]:
    """
    Return the teacher with the highest total workload.

    Parameters
    ----------
    workload : dict of teacher → hours

    Returns
    -------
    (teacher_name, hours)

    Raises
    ------
    ValueError : If the workload dict is empty.
    """
    if not workload:
        raise ValueError("Workload dictionary is empty.")
    return max(workload.items(), key=lambda x: x[1])


def get_min_teacher(workload: Dict[str, int]) -> Tuple[str, int]:
    """
    Return the teacher with the lowest total workload.

    Parameters
    ----------
    workload : dict of teacher → hours

    Returns
    -------
    (teacher_name, hours)

    Raises
    ------
    ValueError : If the workload dict is empty.
    """
    if not workload:
        raise ValueError("Workload dictionary is empty.")
    return min(workload.items(), key=lambda x: x[1])


def find_teacher(workload: Dict[str, int], name: str) -> Optional[Tuple[str, int]]:
    """
    Case-insensitive lookup of a teacher's total workload.

    Parameters
    ----------
    workload : dict of teacher → hours
    name     : Teacher name to search for.

    Returns
    -------
    (teacher_name, hours) or None if not found.
    """
    name_lower = name.strip().lower()
    for teacher, hours in workload.items():
        if teacher.lower() == name_lower:
            return teacher, hours
    return None


def print_workload_table(workload: Dict[str, int]) -> None:
    """
    Pretty-print the workload summary table.

    Parameters
    ----------
    workload : dict of teacher → hours
    """
    print(f"\n{'Teacher':<22} {'Total Hours':>12}")
    print("-" * 36)
    for teacher, hours in sorted(workload.items(), key=lambda x: x[1], reverse=True):
        print(f"{teacher:<22} {hours:>12}")
    print("-" * 36)
    print(f"{'Total records created:':<22} {WorkloadRecord.get_total_records():>12}")
