"""Tests for the configuration loader module."""

import pytest

from besshouka.config.loader import load_recognizer_config, load_operator_config


class TestLoadRecognizerConfig:

    def test_load_valid_config(self, recognizer_yaml_file):
        config = load_recognizer_config(recognizer_yaml_file)
        assert "recognizers" in config
        assert len(config["recognizers"]) == 4

    def test_each_entry_has_required_fields(self, recognizer_yaml_file):
        config = load_recognizer_config(recognizer_yaml_file)
        for entry in config["recognizers"]:
            assert "name" in entry
            assert "entity_type" in entry
            assert "pattern" in entry
            assert "score" in entry

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_recognizer_config(tmp_path / "nonexistent.yaml")

    def test_malformed_yaml_raises(self, invalid_yaml_file):
        with pytest.raises(Exception):  # yaml.YAMLError or ValueError
            load_recognizer_config(invalid_yaml_file)


class TestLoadOperatorConfig:

    def test_load_valid_config(self, operator_yaml_file):
        config = load_operator_config(operator_yaml_file)
        assert "operators" in config

    def test_each_entry_has_method(self, operator_yaml_file):
        config = load_operator_config(operator_yaml_file)
        for entity_type, operator_config in config["operators"].items():
            assert "method" in operator_config

    def test_operator_types_present(self, operator_yaml_file):
        config = load_operator_config(operator_yaml_file)
        operators = config["operators"]
        assert "PERSON" in operators
        assert "PHONE_NUMBER" in operators
        assert "EMAIL" in operators
        assert "MY_NUMBER" in operators

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_operator_config(tmp_path / "nonexistent.yaml")

    def test_malformed_yaml_raises(self, invalid_yaml_file):
        with pytest.raises(Exception):
            load_operator_config(invalid_yaml_file)


class TestConfigValidation:

    def test_missing_required_fields_rejected(self, missing_fields_yaml_file):
        """Entries missing 'pattern' should be caught during validation."""
        with pytest.raises((ValueError, KeyError)):
            config = load_recognizer_config(missing_fields_yaml_file)
            # Validation might happen at load time or need explicit call
