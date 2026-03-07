"""Tests for the encrypt operator."""

from cryptography.fernet import Fernet

from besshouka.anonymizer.operators.encrypt import EncryptOperator


class TestEncryptOperator:

    def setup_method(self):
        self.operator = EncryptOperator()
        self.key = Fernet.generate_key().decode()

    def test_encrypt_returns_different_from_original(self):
        result = self.operator.operate("田中太郎", {"key": self.key})
        assert result != "田中太郎"

    def test_encrypt_roundtrip(self):
        """Encrypting then decrypting should recover the original text."""
        encrypted = self.operator.operate("田中太郎", {"key": self.key})
        f = Fernet(self.key.encode())
        decrypted = f.decrypt(encrypted.encode()).decode()
        assert decrypted == "田中太郎"

    def test_encrypt_different_keys_different_output(self):
        key1 = Fernet.generate_key().decode()
        key2 = Fernet.generate_key().decode()
        result1 = self.operator.operate("田中太郎", {"key": key1})
        result2 = self.operator.operate("田中太郎", {"key": key2})
        assert result1 != result2

    def test_encrypt_empty_input(self):
        result = self.operator.operate("", {"key": self.key})
        f = Fernet(self.key.encode())
        decrypted = f.decrypt(result.encode()).decode()
        assert decrypted == ""

    def test_encrypt_ascii_text(self):
        encrypted = self.operator.operate("tanaka@example.com", {"key": self.key})
        f = Fernet(self.key.encode())
        decrypted = f.decrypt(encrypted.encode()).decode()
        assert decrypted == "tanaka@example.com"
