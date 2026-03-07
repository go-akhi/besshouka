"""Abstract base class for all recognizers."""

from abc import ABC, abstractmethod

from besshouka.models.recognizer_result import RecognizerResult


class BaseRecognizer(ABC):
    """Base class that all recognizers must subclass.

    Subclasses must implement the recognize() method and provide
    name, entity_type(s), and source properties.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The recognizer's unique name."""
        ...

    @property
    @abstractmethod
    def source(self) -> str:
        """The recognizer's source identifier (e.g. 'regex_registry', 'ginza_ner')."""
        ...

    @abstractmethod
    def recognize(self, text: str) -> list[RecognizerResult]:
        """Detect PII in the given text.

        Args:
            text: Normalized text to scan.

        Returns:
            List of RecognizerResult objects for each detected PII span.
        """
        ...
