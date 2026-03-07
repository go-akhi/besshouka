"""Tests for the anonymization engine."""

from besshouka.anonymizer.engine import anonymize
from besshouka.models.recognizer_result import RecognizerResult
from besshouka.models.engine_result import EngineResult


def _make_result(start, end, entity_type, score, source, text):
    return RecognizerResult(
        start=start, end=end, entity_type=entity_type,
        score=score, source=source, text=text,
    )


class TestSingleEntityAnonymization:

    def test_replace_person_name(self):
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        assert "<氏名>" in engine_result.text
        assert "田中太郎" not in engine_result.text
        assert engine_result.text == "<氏名>さんに会いました"

    def test_particle_preserved(self):
        """Particles after the name should not be consumed."""
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        assert engine_result.text.endswith("さんに会いました")

    def test_redact_my_number(self):
        text = "マイナンバーは123456789012です"
        results = [_make_result(7, 19, "MY_NUMBER", 1.0, "regex_registry", "123456789012")]
        config = {"MY_NUMBER": {"method": "redact"}}

        engine_result = anonymize(text, results, config)

        assert "123456789012" not in engine_result.text
        assert engine_result.text == "マイナンバーはです"

    def test_mask_phone_number(self):
        text = "電話番号は090-1234-5678です"
        results = [_make_result(5, 18, "PHONE_NUMBER", 1.0, "regex_registry", "090-1234-5678")]
        config = {"PHONE_NUMBER": {"method": "mask", "char": "*", "from_end": 4}}

        engine_result = anonymize(text, results, config)

        assert "090-1234-" in engine_result.text
        assert engine_result.text == "電話番号は090-1234-****です"


class TestMultipleEntityAnonymization:

    def test_multiple_entities_reverse_loop(self):
        """Replacing from right to left should preserve indices."""
        text = "田中太郎の電話番号は090-1234-5678です"
        results = [
            _make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎"),
            _make_result(10, 23, "PHONE_NUMBER", 1.0, "regex_registry", "090-1234-5678"),
        ]
        config = {
            "PERSON": {"method": "replace", "value": "<氏名>"},
            "PHONE_NUMBER": {"method": "mask", "char": "*", "from_end": 4},
        }

        engine_result = anonymize(text, results, config)

        assert "田中太郎" not in engine_result.text
        assert "<氏名>" in engine_result.text
        assert "090-1234-5678" not in engine_result.text

    def test_three_entities(self):
        text = "田中太郎のメールはtanaka@example.comで電話は090-1234-5678です"
        results = [
            _make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎"),
            _make_result(9, 27, "EMAIL", 1.0, "regex_registry", "tanaka@example.com"),
            _make_result(30, 43, "PHONE_NUMBER", 1.0, "regex_registry", "090-1234-5678"),
        ]
        config = {
            "PERSON": {"method": "replace", "value": "<氏名>"},
            "EMAIL": {"method": "replace", "value": "<メール>"},
            "PHONE_NUMBER": {"method": "replace", "value": "<電話>"},
        }

        engine_result = anonymize(text, results, config)

        assert "田中太郎" not in engine_result.text
        assert "tanaka@example.com" not in engine_result.text
        assert "090-1234-5678" not in engine_result.text


class TestEngineResultAuditTrail:

    def test_audit_trail_has_correct_count(self):
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        assert len(engine_result.items) == 1

    def test_audit_trail_records_operator(self):
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        assert engine_result.items[0].operator == "replace"

    def test_audit_trail_records_original_text(self):
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        assert engine_result.items[0].original_text == "田中太郎"

    def test_audit_trail_new_indices(self):
        """The audit trail should contain indices in the anonymized string."""
        text = "田中太郎さんに会いました"
        results = [_make_result(0, 4, "PERSON", 0.85, "ginza_ner", "田中太郎")]
        config = {"PERSON": {"method": "replace", "value": "<氏名>"}}

        engine_result = anonymize(text, results, config)

        item = engine_result.items[0]
        assert engine_result.text[item.start:item.end] == "<氏名>"


class TestEdgeCases:

    def test_no_results_text_unchanged(self):
        text = "今日はいい天気ですね"
        engine_result = anonymize(text, [], {})
        assert engine_result.text == text
        assert engine_result.items == []

    def test_empty_text(self):
        engine_result = anonymize("", [], {})
        assert engine_result.text == ""
        assert engine_result.items == []

    def test_returns_engine_result_type(self):
        engine_result = anonymize("test", [], {})
        assert isinstance(engine_result, EngineResult)
