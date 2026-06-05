"""
Module   : interface.py
Purpose  : User-facing console interface for the workload management task.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

from typing import List

from task1.analysis import (
    compute_workload,
    find_teacher,
    get_max_teacher,
    get_min_teacher,
    print_workload_table,
)
from task1.models import WorkloadRecord
from task1.storage import CSVStorage, PickleStorage

# Pre-loaded sample data so the task works out-of-the-box
SAMPLE_DATA = [
    WorkloadRecord("Ivanov", "10A", 18),
    WorkloadRecord("Ivanov", "11B", 14),
    WorkloadRecord("Petrov", "9A", 20),
    WorkloadRecord("Petrov", "9B", 16),
    WorkloadRecord("Sidorova", "10B", 12),
    WorkloadRecord("Sidorova", "11A", 10),
    WorkloadRecord("Kozlov", "8A", 22),
    WorkloadRecord("Kozlov", "8B", 18),
    WorkloadRecord("Morozova", "7A", 8),
]


def _input_records() -> List[WorkloadRecord]:
    """Prompt the user to enter workload records manually."""
    records = []
    print("\nEnter workload records. Type 'done' as teacher name to finish.")
    while True:
        teacher = input("  Teacher last name (or 'done'): ").strip()
        if teacher.lower() == "done":
            break
        class_name = input("  Class (e.g. 10A): ").strip()
        while True:
            try:
                hours = int(input("  Hours: "))
                if hours <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  ! Hours must be a positive integer. Try again.")
        try:
            records.append(WorkloadRecord(teacher, class_name, hours))
            print(f"  Added: {records[-1]}")
        except ValueError as exc:
            print(f"  ! Skipped invalid record: {exc}")
    return records


def _choose_storage():
    """Ask the user to choose a storage format."""
    while True:
        choice = input("\nStorage format — [1] CSV  [2] Pickle: ").strip()
        if choice == "1":
            return CSVStorage()
        if choice == "2":
            return PickleStorage()
        print("  ! Please enter 1 or 2.")


def run_task1() -> None:
    """
    Entry point for Task 1 – school workload management.

    Demonstrates:
    - Static and dynamic class attributes
    - Magic methods (__str__, __eq__, __lt__, __add__, __radd__)
    - Properties (getters/setters)
    - Mixins (SerializableMixin, ReprMixin)
    - super() via MRO chain
    - Polymorphism through BaseStorage
    """
    print("\n" + "=" * 60)
    print("  TASK 1 — School Workload Management")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("  [1] Use sample data")
        print("  [2] Enter data manually")
        choice = input("Your choice: ").strip()
        if choice in ("1", "2"):
            break
        print("  ! Enter 1 or 2.")

    records: List[WorkloadRecord] = (
        SAMPLE_DATA if choice == "1" else _input_records()
    )

    if not records:
        print("No records entered. Returning to main menu.")
        return

    # Choose storage and persist
    storage = _choose_storage()
    storage.save(records)
    print(f"\nData saved to: {storage.filepath}")

    # Reload to prove round-trip works
    loaded = storage.load()
    print(f"Loaded {len(loaded)} records from {storage.filepath}")

    # Analysis
    workload = compute_workload(loaded)
    print_workload_table(workload)

    max_teacher, max_hours = get_max_teacher(workload)
    min_teacher, min_hours = get_min_teacher(workload)
    print(f"\nHeaviest workload : {max_teacher} ({max_hours} h)")
    print(f"Lightest workload : {min_teacher} ({min_hours} h)")

    # Lookup a specific teacher
    print()
    while True:
        name = input("Enter a teacher name to look up (or press Enter to skip): ").strip()
        if not name:
            break
        result = find_teacher(workload, name)
        if result:
            print(f"  {result[0]}: {result[1]} hours total")
        else:
            print("  Teacher not found.")
        again = input("Look up another? [y/n]: ").strip().lower()
        if again != "y":
            break

    # Demo: repr and magic methods
    print("\n--- Demo: magic methods ---")
    print(f"repr : {repr(records[0])}")
    print(f"str  : {records[0]}")
    print(f"eq   : records[0] == records[0] → {records[0] == records[0]}")
    if len(records) > 1:
        print(f"lt   : records[0] < records[1] → {records[0] < records[1]}")
    total_hours = sum(records)
    print(f"sum  : total hours across all records = {total_hours}")
    print(f"static total_records = {WorkloadRecord.get_total_records()}")
