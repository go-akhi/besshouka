"""Tests for the mask operator."""

from besshouka.anonymizer.operators.mask import MaskOperator


class TestMaskOperator:

    def setup_method(self):
        self.operator = MaskOperator()

    def test_mask_from_end(self):
        result = self.operator.operate("田中太郎", {"char": "*", "from_end": 2})
        assert result == "田中**"

    def test_mask_all_characters(self):
        result = self.operator.operate("田中太郎", {"char": "*", "from_end": 4})
        assert result == "****"

    def test_mask_credit_card_last_twelve(self):
        """from_end=12 masks the last 12 characters, showing the first 4."""
        result = self.operator.operate("4111111111111111", {"char": "*", "from_end": 12})
        assert result == "4111************"

    def test_mask_with_different_char(self):
        result = self.operator.operate("田中太郎", {"char": "X", "from_end": 2})
        assert result == "田中XX"

    def test_mask_phone_number(self):
        result = self.operator.operate("090-1234-5678", {"char": "*", "from_end": 4})
        assert result == "090-1234-****"

    def test_mask_preserves_length(self):
        original = "田中太郎"
        result = self.operator.operate(original, {"char": "*", "from_end": 2})
        assert len(result) == len(original)

    def test_mask_zero_from_end(self):
        """Masking zero characters from end should return original."""
        result = self.operator.operate("田中太郎", {"char": "*", "from_end": 0})
        assert result == "田中太郎"

    def test_mask_more_than_length(self):
        """Masking more characters than exist should mask everything."""
        result = self.operator.operate("田中", {"char": "*", "from_end": 10})
        assert result == "**"
