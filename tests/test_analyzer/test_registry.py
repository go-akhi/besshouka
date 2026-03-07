"""Tests for the recognizer registry module."""

import pytest

from besshouka.analyzer.registry import load_recognizers, get_all_recognizers
from besshouka.analyzer.recognizers.regex_recognizer import RegexRecognizer


class TestLoadRecognizers:
    """Test loading recognizers from YAML."""

    def test_load_valid_yaml(self, recognizer_yaml_file):
        recognizers = load_recognizers(recognizer_yaml_file)
        assert len(recognizers) == 4  # phone, email, my_number, postal_code

    def test_each_entry_is_regex_recognizer(self, recognizer_yaml_file):
        recognizers = load_recognizers(recognizer_yaml_file)
        for r in recognizers:
            assert isinstance(r, RegexRecognizer)

    def test_recognizer_names(self, recognizer_yaml_file):
        recognizers = load_recognizers(recognizer_yaml_file)
        names = {r.name for r in recognizers}
        assert "japanese_phone" in names
        assert "email" in names
        assert "my_number" in names
        assert "postal_code" in names

    def test_recognizer_entity_types(self, recognizer_yaml_file):
        recognizers = load_recognizers(recognizer_yaml_file)
        types = {r.entity_type for r in recognizers}
        assert "PHONE_NUMBER" in types
        assert "EMAIL" in types
        assert "MY_NUMBER" in types
        assert "POSTAL_CODE" in types

    def test_recognizers_can_match(self, recognizer_yaml_file):
        """Loaded recognizers should actually work."""
        recognizers = load_recognizers(recognizer_yaml_file)
        phone_recognizer = next(r for r in recognizers if r.name == "japanese_phone")
        results = phone_recognizer.recognize("090-1234-5678")
        assert len(results) == 1


class TestLoadRecognizersErrors:
    """Test error handling for invalid YAML."""

    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_recognizers(tmp_path / "nonexistent.yaml")

    def test_missing_required_fields(self, missing_fields_yaml_file):
        """YAML entries missing 'pattern' or 'score' should be rejected."""
        with pytest.raises((ValueError, KeyError)):
            load_recognizers(missing_fields_yaml_file)


class TestGetAllRecognizers:
    """Test retrieval of all registered recognizers."""

    def test_includes_regex_recognizers(self, recognizer_yaml_file):
        load_recognizers(recognizer_yaml_file)
        all_recognizers = get_all_recognizers()
        regex_recognizers = [r for r in all_recognizers if isinstance(r, RegexRecognizer)]
        assert len(regex_recognizers) >= 4

    def test_returns_list(self, recognizer_yaml_file):
        load_recognizers(recognizer_yaml_file)
        all_recognizers = get_all_recognizers()
        assert isinstance(all_recognizers, list)
