"""Tests for OperatorResult and EngineResult data models."""

from besshouka.models.engine_result import OperatorResult, EngineResult


class TestOperatorResultCreation:
    """Test OperatorResult instantiation."""

    def test_create_with_all_fields(self):
        result = OperatorResult(
            entity_type="PERSON",
            start=0,
            end=4,
            operator="replace",
            original_text="田中太郎",
        )
        assert result.entity_type == "PERSON"
        assert result.start == 0
        assert result.end == 4
        assert result.operator == "replace"
        assert result.original_text == "田中太郎"

    def test_indices_reflect_anonymized_string(self):
        """start/end should refer to positions in the anonymized output, not the original."""
        result = OperatorResult(
            entity_type="PERSON",
            start=0,
            end=4,  # e.g., len("<氏名>") = 4
            operator="replace",
            original_text="田中太郎",
        )
        anonymized = "<氏名>さんに会いました"
        assert anonymized[result.start:result.end] == "<氏名>"


class TestEngineResultCreation:
    """Test EngineResult instantiation."""

    def test_create_with_text_and_items(self):
        op_result = OperatorResult(
            entity_type="PERSON",
            start=0,
            end=4,
            operator="replace",
            original_text="田中太郎",
        )
        engine_result = EngineResult(
            text="<氏名>さんに会いました",
            items=[op_result],
        )
        assert engine_result.text == "<氏名>さんに会いました"
        assert len(engine_result.items) == 1
        assert engine_result.items[0].original_text == "田中太郎"

    def test_empty_items_when_no_pii(self):
        engine_result = EngineResult(
            text="今日はいい天気ですね",
            items=[],
        )
        assert engine_result.text == "今日はいい天気ですね"
        assert engine_result.items == []

    def test_multiple_items(self):
        items = [
            OperatorResult(
                entity_type="PERSON", start=0, end=4,
                operator="replace", original_text="田中太郎",
            ),
            OperatorResult(
                entity_type="PHONE_NUMBER", start=10, end=23,
                operator="mask", original_text="090-1234-5678",
            ),
        ]
        engine_result = EngineResult(
            text="<氏名>さんの電話番号は090-****-****です",
            items=items,
        )
        assert len(engine_result.items) == 2
        assert engine_result.items[0].entity_type == "PERSON"
        assert engine_result.items[1].entity_type == "PHONE_NUMBER"
