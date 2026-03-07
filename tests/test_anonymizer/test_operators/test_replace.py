"""Tests for the replace operator."""

from besshouka.anonymizer.operators.replace import ReplaceOperator


class TestReplaceOperator:

    def setup_method(self):
        self.operator = ReplaceOperator()

    def test_replace_with_japanese_tag(self):
        result = self.operator.operate("田中太郎", {"value": "<氏名>"})
        assert result == "<氏名>"

    def test_replace_with_english_tag(self):
        result = self.operator.operate("田中太郎", {"value": "<PERSON>"})
        assert result == "<PERSON>"

    def test_replace_ignores_original_text(self):
        """The original text should not affect the output."""
        result1 = self.operator.operate("田中太郎", {"value": "<氏名>"})
        result2 = self.operator.operate("山田花子", {"value": "<氏名>"})
        assert result1 == result2

    def test_replace_with_empty_value(self):
        result = self.operator.operate("田中太郎", {"value": ""})
        assert result == ""

    def test_replace_preserves_value_exactly(self):
        result = self.operator.operate("test", {"value": "【個人名】"})
        assert result == "【個人名】"
