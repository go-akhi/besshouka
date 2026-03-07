"""Tests for the conflict resolution module."""

from besshouka.analyzer.conflict_resolution import resolve_conflicts
from besshouka.models.recognizer_result import RecognizerResult


def _make_result(start, end, entity_type, score, source, text):
    """Helper to create RecognizerResult instances."""
    return RecognizerResult(
        start=start, end=end, entity_type=entity_type,
        score=score, source=source, text=text,
    )


class TestLongestMatchWins:
    """Rule 1: If one span contains another, keep the longer one."""

    def test_nested_span_keeps_longer(self):
        results = [
            _make_result(0, 7, "ORGANIZATION", 0.80, "ginza_ner", "山田クリニック"),
            _make_result(0, 2, "PERSON", 0.90, "ginza_ner", "山田"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0].entity_type == "ORGANIZATION"
        assert resolved[0].text == "山田クリニック"

    def test_inner_span_removed(self):
        results = [
            _make_result(0, 10, "ORGANIZATION", 0.75, "ginza_ner", "東京都渋谷区渋谷"),
            _make_result(0, 3, "LOCATION", 0.85, "ginza_ner", "東京都"),
            _make_result(3, 6, "LOCATION", 0.80, "ginza_ner", "渋谷区"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0].end - resolved[0].start == 10


class TestScoreTieBreaker:
    """Rule 2: If spans are equal length, keep the higher score."""

    def test_equal_length_higher_score_wins(self):
        results = [
            _make_result(0, 4, "PERSON", 0.70, "ginza_ner", "田中太郎"),
            _make_result(0, 4, "ORGANIZATION", 0.90, "ginza_ner", "田中太郎"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0].score == 0.90
        assert resolved[0].entity_type == "ORGANIZATION"

    def test_exact_same_score_still_resolves(self):
        """When scores are identical, one should still be chosen (no duplicates)."""
        results = [
            _make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎"),
            _make_result(0, 4, "ORGANIZATION", 0.85, "ginza_ner", "田中太郎"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1


class TestStructuredOverUnstructured:
    """Rule 3: Regex (structured/deterministic) wins over GiNZA (unstructured/probabilistic)."""

    def test_regex_wins_over_ginza_same_span(self):
        results = [
            _make_result(0, 12, "MY_NUMBER", 1.0, "regex_registry", "123456789012"),
            _make_result(0, 12, "NUMBER", 0.60, "ginza_ner", "123456789012"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0].source == "regex_registry"
        assert resolved[0].entity_type == "MY_NUMBER"

    def test_regex_wins_even_with_lower_length(self):
        """Structured > unstructured even in partial overlap scenarios."""
        results = [
            _make_result(0, 12, "MY_NUMBER", 1.0, "regex_registry", "123456789012"),
            _make_result(0, 12, "QUANTITY", 0.95, "ginza_ner", "123456789012"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0].source == "regex_registry"


class TestNonOverlapping:
    """Non-overlapping results should all be preserved."""

    def test_non_overlapping_all_kept(self):
        results = [
            _make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎"),
            _make_result(10, 23, "PHONE_NUMBER", 1.0, "regex_registry", "090-1234-5678"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 2

    def test_adjacent_entities_preserved(self):
        """Entities that are adjacent (end of one == start of next) should both be kept."""
        results = [
            _make_result(0, 3, "LOCATION", 0.80, "ginza_ner", "東京都"),
            _make_result(3, 6, "LOCATION", 0.80, "ginza_ner", "渋谷区"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 2

    def test_empty_input(self):
        resolved = resolve_conflicts([])
        assert resolved == []

    def test_single_result(self):
        results = [
            _make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 1


class TestMultipleOverlappingGroups:
    """Multiple independent overlapping groups resolved independently."""

    def test_two_groups_resolved_independently(self):
        results = [
            # Group 1: overlapping at positions 0-7
            _make_result(0, 7, "ORGANIZATION", 0.80, "ginza_ner", "山田クリニック"),
            _make_result(0, 2, "PERSON", 0.90, "ginza_ner", "山田"),
            # Group 2: overlapping at positions 20-32
            _make_result(20, 32, "MY_NUMBER", 1.0, "regex_registry", "123456789012"),
            _make_result(20, 32, "QUANTITY", 0.60, "ginza_ner", "123456789012"),
        ]
        resolved = resolve_conflicts(results)
        assert len(resolved) == 2
        types = {r.entity_type for r in resolved}
        assert "ORGANIZATION" in types
        assert "MY_NUMBER" in types
