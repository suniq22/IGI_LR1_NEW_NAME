"""
Module   : analyzer.py
Purpose  : Text analysis using regular expressions.
           Covers: sentence counting, average lengths, smileys,
           lowercase-starting words, punctuation, MAC validation,
           word statistics, ZIP archiving.
Lab      : LR4 - Object-Oriented Programming in Python
Version  : 1.0
Developer: Bryaginya Vladislav
Date     : 2026-04-16
"""

import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ── Mixins ────────────────────────────────────────────────────────────────────

class LogMixin:
    """Mixin that adds a simple log() helper for console output."""

    def log(self, message: str) -> None:
        """Print a labelled log message."""
        print(f"[{self.__class__.__name__}] {message}")


class SaveMixin:
    """Mixin that adds save_to_file() capability."""

    def save_to_file(self, path: Path, content: str) -> None:
        """
        Write *content* to *path* (UTF-8).

        Parameters
        ----------
        path    : Destination file path.
        content : Text content to write.
        """
        path.write_text(content, encoding="utf-8")


# ── Core analyser ─────────────────────────────────────────────────────────────

class TextAnalyzer(LogMixin, SaveMixin):
    """
    Analyses a plain-text string and produces various statistics.

    Demonstrates:
    - Static and dynamic attributes
    - Properties (getter only – text is read-only after construction)
    - Mixins (LogMixin, SaveMixin)
    - Magic methods (__str__, __len__, __repr__)
    - Polymorphism through subclassing
    """

    # Static attribute – counts how many analyser instances have been created
    _instance_count: int = 0

    # Regex patterns compiled once at class level (dynamic class attributes)
    _RE_SENTENCES_ALL = re.compile(r"[^.!?]*[.!?]", re.DOTALL)
    _RE_DECLARATIVE   = re.compile(r"[^.!?]*\.", re.DOTALL)
    _RE_INTERROGATIVE = re.compile(r"[^.!?]*\?", re.DOTALL)
    _RE_IMPERATIVE    = re.compile(r"[^.!?]*!", re.DOTALL)
    _RE_WORDS         = re.compile(r"\b[a-zA-Z]+\b")
    # Smiley: starts with ; or :, then zero or more -, then 1+ identical brackets
    _RE_SMILEY        = re.compile(r"[;:]-*([()[\]])\1*")
    _RE_LOWERCASE_START = re.compile(r"\b[a-z][a-zA-Z]*\b")
    _RE_PUNCTUATION   = re.compile(r"[.,!?;:\'\"\(\)\[\]\{\}\-—]")
    _RE_MAC_STRICT    = re.compile(
        r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$"
    )

    def __init__(self, text: str) -> None:
        """
        Initialise the analyser with *text*.

        Parameters
        ----------
        text : The source text to analyse.

        Raises
        ------
        ValueError : If *text* is empty or not a string.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")
        self._text = text
        TextAnalyzer._instance_count += 1

    # ── Property ──────────────────────────────────────────────────────────

    @property
    def text(self) -> str:
        """The source text (read-only)."""
        return self._text

    # ── Class method ──────────────────────────────────────────────────────

    @classmethod
    def get_instance_count(cls) -> int:
        """Return the total number of TextAnalyzer instances created."""
        return cls._instance_count

    @classmethod
    def from_file(cls, path: Path) -> "TextAnalyzer":
        """
        Create a TextAnalyzer from a text file.

        Parameters
        ----------
        path : Path to the UTF-8 text file.

        Raises
        ------
        FileNotFoundError : If path does not exist.
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")
        text = Path(path).read_text(encoding="utf-8")
        return cls(text)

    # ── Sentence-level statistics ─────────────────────────────────────────

    def count_sentences(self) -> int:
        """Return total number of sentences in the text."""
        return len(self._RE_SENTENCES_ALL.findall(self._text))

    def count_by_type(self) -> Dict[str, int]:
        """
        Count sentences by type.

        Returns
        -------
        dict with keys 'declarative', 'interrogative', 'imperative'
        """
        return {
            "declarative":   len(self._RE_DECLARATIVE.findall(self._text)),
            "interrogative": len(self._RE_INTERROGATIVE.findall(self._text)),
            "imperative":    len(self._RE_IMPERATIVE.findall(self._text)),
        }

    def avg_sentence_length(self) -> float:
        """
        Return the average sentence length in characters (words only, no spaces).

        Only alphabetic word characters are counted.
        """
        sentences = self._RE_SENTENCES_ALL.findall(self._text)
        if not sentences:
            return 0.0
        lengths = [
            sum(len(w) for w in self._RE_WORDS.findall(s))
            for s in sentences
        ]
        return sum(lengths) / len(lengths)

    # ── Word-level statistics ─────────────────────────────────────────────

    def get_words(self) -> List[str]:
        """Return all words found in the text."""
        return self._RE_WORDS.findall(self._text)

    def avg_word_length(self) -> float:
        """Return the average word length in characters."""
        words = self.get_words()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    def word_count(self) -> int:
        """Return the total number of words in the text."""
        return len(self.get_words())

    def longest_word(self) -> Tuple[str, int]:
        """
        Return the longest word and its 1-based position (index).

        Returns
        -------
        (word, 1-based position) or ('', 0) if no words.
        """
        words = self.get_words()
        if not words:
            return ("", 0)
        longest = max(words, key=len)
        return (longest, words.index(longest) + 1)

    def odd_words(self) -> List[str]:
        """Return every word at an odd position (1st, 3rd, 5th …)."""
        return [w for i, w in enumerate(self.get_words()) if i % 2 == 0]

    # ── Special patterns ──────────────────────────────────────────────────

    def find_smileys(self) -> List[str]:
        """
        Find all smileys in the text.

        A smiley matches: ``[;:]-*([()\\[\\]])\\1*``
        i.e. starts with ; or :, then zero or more -, then one or more
        identical bracket characters.

        Returns
        -------
        list of matched smiley strings
        """
        return self._RE_SMILEY.findall(self._text)

    def _find_smileys_full(self) -> List[str]:
        """Return full smiley match strings (not just the capture group)."""
        return [m.group(0) for m in self._RE_SMILEY.finditer(self._text)]

    def lowercase_words(self) -> List[str]:
        """Return all words that begin with a lowercase ASCII letter."""
        return self._RE_LOWERCASE_START.findall(self._text)

    def punctuation_marks(self) -> List[str]:
        """Return all punctuation characters found in the text."""
        return self._RE_PUNCTUATION.findall(self._text)

    # ── MAC address ───────────────────────────────────────────────────────

    @classmethod
    def is_valid_mac(cls, address: str) -> bool:
        """
        Check whether *address* is a valid MAC address.

        Valid format: XX:XX:XX:XX:XX:XX where X ∈ [0-9A-Fa-f].

        Parameters
        ----------
        address : String to validate.

        Returns
        -------
        bool
        """
        return bool(cls._RE_MAC_STRICT.match(address.strip()))

    # ── Reporting ─────────────────────────────────────────────────────────

    def full_report(self) -> str:
        """
        Build a comprehensive text report of all analysis results.

        Returns
        -------
        Formatted multi-line string.
        """
        types = self.count_by_type()
        lword, lpos = self.longest_word()
        smileys = self._find_smileys_full()
        lines = [
            "=" * 60,
            "  TEXT ANALYSIS REPORT",
            "=" * 60,
            f"Total sentences       : {self.count_sentences()}",
            f"  Declarative         : {types['declarative']}",
            f"  Interrogative       : {types['interrogative']}",
            f"  Imperative          : {types['imperative']}",
            f"Avg sentence length   : {self.avg_sentence_length():.2f} chars (word chars only)",
            f"Total words           : {self.word_count()}",
            f"Avg word length       : {self.avg_word_length():.2f} chars",
            f"Smileys found ({len(smileys)})    : {smileys}",
            "",
            f"Lowercase-start words : {self.lowercase_words()}",
            "",
            f"Punctuation marks     : {self.punctuation_marks()}",
            "",
            f"Longest word          : '{lword}' at position {lpos}",
            f"Odd-position words    : {self.odd_words()}",
            "=" * 60,
        ]
        return "\n".join(lines)

    # ── Magic methods ─────────────────────────────────────────────────────

    def __len__(self) -> int:
        """Return the number of characters in the text."""
        return len(self._text)

    def __str__(self) -> str:
        return f"TextAnalyzer(chars={len(self._text)}, words={self.word_count()})"

    def __repr__(self) -> str:
        preview = self._text[:30].replace("\n", " ")
        return f"TextAnalyzer(text={preview!r}...)"


# ── Specialised subclass – demonstrates polymorphism ──────────────────────────

class MACFocusedAnalyzer(TextAnalyzer):
    """
    Extends TextAnalyzer to extract and validate all MAC-like tokens.

    Demonstrates super() and polymorphism.
    """

    _RE_MAC_CANDIDATE = re.compile(
        r"\b[0-9A-Fa-z]{2}(?::[0-9A-Fa-z]{2}){5}\b"
    )

    def __init__(self, text: str) -> None:
        super().__init__(text)   # super() call

    def find_mac_candidates(self) -> List[str]:
        """Return all colon-separated hex-like tokens (valid OR invalid)."""
        return self._RE_MAC_CANDIDATE.findall(self._text)

    def validate_all_macs(self) -> Dict[str, bool]:
        """
        Return a dict mapping each MAC candidate → is_valid.

        Overrides (polymorphically extends) base functionality.
        """
        return {
            candidate: self.is_valid_mac(candidate)
            for candidate in self.find_mac_candidates()
        }

    def full_report(self) -> str:
        """Return base report plus MAC validation section."""
        base = super().full_report()  # super() call
        mac_results = self.validate_all_macs()
        lines = [base, "", "  MAC ADDRESS VALIDATION"]
        lines.append("-" * 40)
        for addr, valid in mac_results.items():
            status = "VALID" if valid else "INVALID"
            lines.append(f"  {addr:<25} → {status}")
        if not mac_results:
            lines.append("  No MAC-like tokens found.")
        lines.append("=" * 60)
        return "\n".join(lines)


# ── ZIP helper ────────────────────────────────────────────────────────────────

def archive_result(result_path: Path, archive_path: Path) -> None:
    """
    Add *result_path* to a ZIP archive at *archive_path*.

    Parameters
    ----------
    result_path  : File to archive.
    archive_path : Destination ZIP path.
    """
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(result_path, arcname=result_path.name)


def print_archive_info(archive_path: Path) -> None:
    """
    Print information about every file inside the ZIP archive.

    Parameters
    ----------
    archive_path : Path to the ZIP archive.
    """
    with zipfile.ZipFile(archive_path, "r") as zf:
        print(f"\nArchive: {archive_path}")
        print(f"{'Filename':<30} {'Size':>10} {'Compressed':>12}")
        print("-" * 56)
        for info in zf.infolist():
            print(
                f"{info.filename:<30} "
                f"{info.file_size:>10} "
                f"{info.compress_size:>12}"
            )
