"""
Module   : storage.py
Purpose  : CSV and Pickle persistence for WorkloadRecord objects.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

import csv
import pickle
from pathlib import Path
from typing import List

from task1.models import WorkloadRecord

# Default file paths (same directory as this module)
_DIR = Path(__file__).parent
CSV_PATH = _DIR / "workload.csv"
PICKLE_PATH = _DIR / "workload.pkl"


class BaseStorage:
    """Abstract base for storage backends."""

    def save(self, records: List[WorkloadRecord]) -> None:
        """Persist records to storage."""
        raise NotImplementedError

    def load(self) -> List[WorkloadRecord]:
        """Load records from storage."""
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(path={self.filepath})"

    def __repr__(self) -> str:
        return self.__str__()


class CSVStorage(BaseStorage):
    """
    Stores WorkloadRecord objects in a CSV file.

    Parameters
    ----------
    filepath : Path or str
        Destination CSV file path.
    """

    FIELDNAMES = ["teacher", "class_name", "hours"]

    def __init__(self, filepath: Path = CSV_PATH) -> None:
        self.filepath = Path(filepath)

    def save(self, records: List[WorkloadRecord]) -> None:
        """
        Write *records* to a CSV file, overwriting any existing content.

        Parameters
        ----------
        records : list of WorkloadRecord
        """
        with open(self.filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for rec in records:
                writer.writerow(rec.to_dict())

    def load(self) -> List[WorkloadRecord]:
        """
        Read records from the CSV file.

        Returns
        -------
        list of WorkloadRecord – empty list if file does not exist.
        """
        if not self.filepath.exists():
            return []
        with open(self.filepath, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            return [WorkloadRecord.from_dict(row) for row in reader]


class PickleStorage(BaseStorage):
    """
    Stores WorkloadRecord objects using Python's pickle serialiser.

    Parameters
    ----------
    filepath : Path or str
        Destination .pkl file path.
    """

    def __init__(self, filepath: Path = PICKLE_PATH) -> None:
        self.filepath = Path(filepath)

    def save(self, records: List[WorkloadRecord]) -> None:
        """
        Serialise *records* to a binary pickle file.

        Parameters
        ----------
        records : list of WorkloadRecord
        """
        with open(self.filepath, "wb") as fh:
            pickle.dump(records, fh)

    def load(self) -> List[WorkloadRecord]:
        """
        Deserialise records from the pickle file.

        Returns
        -------
        list of WorkloadRecord – empty list if file does not exist.
        """
        if not self.filepath.exists():
            return []
        with open(self.filepath, "rb") as fh:
            return pickle.load(fh)
