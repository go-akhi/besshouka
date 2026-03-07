"""Tests for the redact operator."""

from besshouka.anonymizer.operators.redact import RedactOperator


class TestRedactOperator:

    def setup_method(self):
        self.operator = RedactOperator()

    def test_redact_returns_empty(self):
        result = self.operator.operate("田中太郎", {})
        assert result == ""

    def test_redact_any_text(self):
        result = self.operator.operate("090-1234-5678", {})
        assert result == ""

    def test_redact_empty_input(self):
        result = self.operator.operate("", {})
        assert result == ""

    def test_redact_ignores_params(self):
        result = self.operator.operate("test", {"key": "value"})
        assert result == ""
