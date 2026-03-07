"""Anonymization engine \u2014 applies operators to detected PII using a reverse-loop algorithm."""

from besshouka.models.recognizer_result import RecognizerResult
from besshouka.models.engine_result import OperatorResult, EngineResult
from besshouka.anonymizer.operators.replace import ReplaceOperator
from besshouka.anonymizer.operators.mask import MaskOperator
from besshouka.anonymizer.operators.redact import RedactOperator
from besshouka.anonymizer.operators.hash import HashOperator
from besshouka.anonymizer.operators.encrypt import EncryptOperator
from besshouka.anonymizer.operators.keep import KeepOperator
from besshouka.anonymizer.operators.custom import CustomOperator
from besshouka.anonymizer.operators.base import BaseOperator


_OPERATORS: dict[str, BaseOperator] = {
    "replace": ReplaceOperator(),
    "mask": MaskOperator(),
    "redact": RedactOperator(),
    "hash": HashOperator(),
    "encrypt": EncryptOperator(),
    "keep": KeepOperator(),
    "custom": CustomOperator(),
}


def _get_operator(name: str) -> BaseOperator:
    """Look up an operator by name."""
    if name not in _OPERATORS:
        raise ValueError(f"Unknown operator: {name}")
    return _OPERATORS[name]


def anonymize(
    text: str,
    results: list[RecognizerResult],
    operator_config: dict,
) -> EngineResult:
    """Apply anonymization operators to detected PII spans.

    Processes results from right to left (reverse-loop) so that replacements
    don't shift the indices of earlier spans.

    Args:
        text: The original text.
        results: List of RecognizerResult objects (PII detections).
        operator_config: Mapping of entity_type -> operator config dict.
                         Each value must have a 'method' key.

    Returns:
        EngineResult with the anonymized text and an audit trail.
    """
    if not results:
        return EngineResult(text=text, items=[])

    # Sort descending by start position for right-to-left processing
    sorted_results = sorted(results, key=lambda r: r.start, reverse=True)

    anonymized = text
    audit_items: list[OperatorResult] = []

    for result in sorted_results:
        config = operator_config.get(result.entity_type, {})
        method = config.get("method", "keep")
        operator = _get_operator(method)

        replacement = operator.operate(result.text, config)

        # Replace the span in the text
        anonymized = anonymized[:result.start] + replacement + anonymized[result.end:]

        audit_items.append(
            OperatorResult(
                entity_type=result.entity_type,
                start=result.start,
                end=result.start + len(replacement),
                operator=method,
                original_text=result.text,
            )
        )

    # Reverse audit items so they're in left-to-right order
    audit_items.reverse()

    return EngineResult(text=anonymized, items=audit_items)
