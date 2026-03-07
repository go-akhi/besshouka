"""Data model for PII detection results returned by recognizers."""

from dataclasses import dataclass, field


@dataclass
class RecognizerResult:
    """A single PII detection result from any recognizer.

    Attributes:
        start: Character offset of the start of the PII in the text.
        end: Character offset of the end of the PII in the text.
        entity_type: Standardized PII category (e.g. PERSON, PHONE_NUMBER).
        score: Confidence level from 0.0 to 1.0.
        source: Which recognizer produced this result.
        text: The actual matched snippet.
        recognition_metadata: Optional extra info (e.g. region, sub-type).
    """

    start: int
    end: int
    entity_type: str
    score: float
    source: str
    text: str
    recognition_metadata: dict = field(default_factory=dict)
