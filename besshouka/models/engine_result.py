"""Data models for anonymization engine output."""

from dataclasses import dataclass, field


@dataclass
class OperatorResult:
    """Audit trail entry for a single anonymization operation.

    Attributes:
        entity_type: The PII category that was anonymized.
        start: Character offset in the anonymized string (new index).
        end: Character offset in the anonymized string (new index).
        operator: Which operator was applied (e.g. replace, mask, redact).
        original_text: The original PII snippet before anonymization.
    """

    entity_type: str
    start: int
    end: int
    operator: str
    original_text: str


@dataclass
class EngineResult:
    """Output of the anonymization engine.

    Attributes:
        text: The fully anonymized string.
        items: Audit trail of every change made.
    """

    text: str
    items: list[OperatorResult] = field(default_factory=list)
