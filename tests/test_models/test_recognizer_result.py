"""Tests for the RecognizerResult data model."""

from besshouka.models.recognizer_result import RecognizerResult


class TestRecognizerResultCreation:
    """Test RecognizerResult instantiation."""

    def test_create_with_all_fields(self):
        result = RecognizerResult(
            start=0,
            end=4,
            entity_type="PERSON",
            score=0.95,
            source="ginza_ner",
            text="田中太郎",
            recognition_metadata={"region": "Tokyo"},
        )
        assert result.start == 0
        assert result.end == 4
        assert result.entity_type == "PERSON"
        assert result.score == 0.95
        assert result.source == "ginza_ner"
        assert result.text == "田中太郎"
        assert result.recognition_metadata == {"region": "Tokyo"}

    def test_create_with_required_fields_only(self):
        result = RecognizerResult(
            start=0,
            end=4,
            entity_type="PERSON",
            score=0.95,
            source="ginza_ner",
            text="田中太郎",
        )
        assert result.recognition_metadata == {}

    def test_default_metadata_is_empty_dict(self):
        result = RecognizerResult(
            start=0,
            end=4,
            entity_type="PERSON",
            score=1.0,
            source="regex_registry",
            text="田中太郎",
        )
        assert result.recognition_metadata == {}
        assert isinstance(result.recognition_metadata, dict)


class TestRecognizerResultFields:
    """Test field access and semantics."""

    def test_span_length(self):
        result = RecognizerResult(
            start=5,
            end=18,
            entity_type="PHONE_NUMBER",
            score=1.0,
            source="regex_registry",
            text="090-1234-5678",
        )
        assert result.end - result.start == 13

    def test_score_range_valid(self):
        """Score should be between 0.0 and 1.0."""
        result = RecognizerResult(
            start=0, end=4, entity_type="PERSON",
            score=0.5, source="ginza_ner", text="田中太郎",
        )
        assert 0.0 <= result.score <= 1.0

    def test_regex_source_score_is_one(self):
        """Regex recognizer results should always have score 1.0."""
        result = RecognizerResult(
            start=0, end=13, entity_type="PHONE_NUMBER",
            score=1.0, source="regex_registry", text="090-1234-5678",
        )
        assert result.score == 1.0

    def test_entity_type_is_string(self):
        result = RecognizerResult(
            start=0, end=4, entity_type="PERSON",
            score=0.85, source="ginza_ner", text="田中太郎",
        )
        assert isinstance(result.entity_type, str)

    def test_text_matches_span_content(self):
        """The text field should contain the actual matched snippet."""
        original = "田中太郎さんに会いました"
        result = RecognizerResult(
            start=0, end=4, entity_type="PERSON",
            score=0.85, source="ginza_ner", text="田中太郎",
        )
        assert original[result.start:result.end] == result.text
