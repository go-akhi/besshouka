"""Tests for the keep operator."""

from besshouka.anonymizer.operators.keep import KeepOperator


class TestKeepOperator:

    def setup_method(self):
        self.operator = KeepOperator()

    def test_keep_returns_original(self):
        result = self.operator.operate("田中太郎", {})
        assert result == "田中太郎"

    def test_keep_with_ascii(self):
        result = self.operator.operate("tanaka@example.com", {})
        assert result == "tanaka@example.com"

    def test_keep_empty_input(self):
        result = self.operator.operate("", {})
        assert result == ""

    def test_keep_ignores_params(self):
        result = self.operator.operate("田中太郎", {"key": "value"})
        assert result == "田中太郎"
