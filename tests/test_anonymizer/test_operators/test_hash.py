"""Tests for the hash operator."""

import re

from besshouka.anonymizer.operators.hash import HashOperator


class TestHashOperator:

    def setup_method(self):
        self.operator = HashOperator()

    def test_hash_returns_hex_string(self):
        result = self.operator.operate("田中太郎", {"salt": "test_salt"})
        assert re.match(r"^[a-f0-9]+$", result)

    def test_hash_is_deterministic_with_same_salt(self):
        result1 = self.operator.operate("田中太郎", {"salt": "salt1"})
        result2 = self.operator.operate("田中太郎", {"salt": "salt1"})
        assert result1 == result2

    def test_hash_differs_with_different_salt(self):
        result1 = self.operator.operate("田中太郎", {"salt": "salt1"})
        result2 = self.operator.operate("田中太郎", {"salt": "salt2"})
        assert result1 != result2

    def test_hash_differs_for_different_input(self):
        result1 = self.operator.operate("田中太郎", {"salt": "salt"})
        result2 = self.operator.operate("山田花子", {"salt": "salt"})
        assert result1 != result2

    def test_hash_is_sha256_length(self):
        """SHA-256 produces a 64-character hex string."""
        result = self.operator.operate("田中太郎", {"salt": "salt"})
        assert len(result) == 64

    def test_hash_empty_input(self):
        result = self.operator.operate("", {"salt": "salt"})
        assert re.match(r"^[a-f0-9]{64}$", result)
