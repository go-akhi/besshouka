"""Conflict resolution for overlapping PII detections.

Rules (in priority order):
1. Longest match wins \u2014 if one span contains another, keep the longer.
2. Score tie-breaker \u2014 if spans are equal length, keep the higher score.
3. Structured > unstructured \u2014 regex (deterministic) wins over GiNZA (probabilistic).
"""

from besshouka.models.recognizer_result import RecognizerResult


_STRUCTURED_SOURCES = {"regex_registry", "custom"}


def _spans_overlap(a: RecognizerResult, b: RecognizerResult) -> bool:
    """Check if two spans overlap (not just adjacent)."""
    return a.start < b.end and b.start < a.end


def _pick_winner(a: RecognizerResult, b: RecognizerResult) -> RecognizerResult:
    """Given two overlapping results, pick the winner.

    Rule 1: Longest match wins.
    Rule 2: Score tie-breaker (if equal length).
    Rule 3: Structured > unstructured (if equal length and score).
    """
    len_a = a.end - a.start
    len_b = b.end - b.start

    # Rule 1: longest match
    if len_a != len_b:
        return a if len_a > len_b else b

    # Rule 2: score tie-breaker
    if a.score != b.score:
        return a if a.score > b.score else b

    # Rule 3: structured > unstructured
    a_structured = a.source in _STRUCTURED_SOURCES
    b_structured = b.source in _STRUCTURED_SOURCES
    if a_structured and not b_structured:
        return a
    if b_structured and not a_structured:
        return b

    # Fallback: keep the first one
    return a


def resolve_conflicts(results: list[RecognizerResult]) -> list[RecognizerResult]:
    """Resolve overlapping detections, returning a non-overlapping set.

    Args:
        results: Raw list of RecognizerResult objects from all recognizers.

    Returns:
        Filtered list with overlaps resolved according to the priority rules.
    """
    if not results:
        return []

    # Sort by start position, then by descending length for stable processing
    sorted_results = sorted(results, key=lambda r: (r.start, -(r.end - r.start)))

    resolved = [sorted_results[0]]

    for current in sorted_results[1:]:
        last = resolved[-1]

        if _spans_overlap(last, current):
            # Replace the last entry with the winner
            winner = _pick_winner(last, current)
            resolved[-1] = winner
        else:
            resolved.append(current)

    return resolved
