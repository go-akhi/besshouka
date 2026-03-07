"""Generic regex-based recognizer instantiated per YAML entry."""

import re

from besshouka.analyzer.recognizers.base import BaseRecognizer
from besshouka.models.recognizer_result import RecognizerResult


class RegexRecognizer(BaseRecognizer):
    """A recognizer driven by a single regex pattern.

    One instance is created per entry in the YAML recognizer registry.
    """

    def __init__(
        self,
        name: str,
        entity_type: str,
        pattern: str,
        score: float,
        source: str,
    ):
        self._name = name
        self._entity_type = entity_type
        self._pattern = re.compile(pattern)
        self._score = score
        self._source = source

    @property
    def name(self) -> str:
        return self._name

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def source(self) -> str:
        return self._source

    def recognize(self, text: str) -> list[RecognizerResult]:
        """Run the compiled regex against the text and return all matches."""
        results = []
        for match in self._pattern.finditer(text):
            results.append(
                RecognizerResult(
                    start=match.start(),
                    end=match.end(),
                    entity_type=self._entity_type,
                    score=self._score,
                    source=self._source,
                    text=match.group(),
                )
            )
        return results
