"""Tests for the Typer CLI interface."""

import pytest
from typer.testing import CliRunner

from besshouka.cli import app


runner = CliRunner()


class TestAnonymizeCommand:

    def test_anonymize_inline_text(self):
        result = runner.invoke(app, ["anonymize", "電話番号は090-1234-5678です"])
        assert result.exit_code == 0
        assert "090-1234-5678" not in result.stdout

    def test_anonymize_with_input_output_files(self, tmp_path):
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text("電話番号は090-1234-5678です", encoding="utf-8")

        result = runner.invoke(app, [
            "anonymize",
            "--input", str(input_file),
            "--output", str(output_file),
        ])

        assert result.exit_code == 0
        assert output_file.exists()
        output_text = output_file.read_text(encoding="utf-8")
        assert "090-1234-5678" not in output_text

    def test_anonymize_with_custom_rules(self, tmp_path):
        rules_file = tmp_path / "rules.yaml"
        rules_file.write_text(
            "operators:\n  PHONE_NUMBER:\n    method: redact\n",
            encoding="utf-8",
        )

        result = runner.invoke(app, [
            "anonymize",
            "--rules", str(rules_file),
            "電話番号は090-1234-5678です",
        ])

        assert result.exit_code == 0

    def test_anonymize_with_custom_recognizers(self, tmp_path):
        recognizers_file = tmp_path / "recognizers.yaml"
        recognizers_file.write_text(
            "recognizers:\n"
            "  - name: test_phone\n"
            "    entity_type: PHONE_NUMBER\n"
            "    pattern: '0\\d{1,4}-?\\d{1,4}-?\\d{4}'\n"
            "    score: 1.0\n"
            "    source: regex_registry\n",
            encoding="utf-8",
        )

        result = runner.invoke(app, [
            "anonymize",
            "--recognizers", str(recognizers_file),
            "電話番号は090-1234-5678です",
        ])

        assert result.exit_code == 0

    def test_anonymize_no_pii(self):
        result = runner.invoke(app, ["anonymize", "今日はいい天気ですね"])
        assert result.exit_code == 0
        assert "今日はいい天気ですね" in result.stdout


class TestAnalyzeCommand:

    def test_analyze_shows_detections(self):
        result = runner.invoke(app, ["analyze", "電話番号は090-1234-5678です"])
        assert result.exit_code == 0
        assert "PHONE_NUMBER" in result.stdout

    def test_analyze_no_pii(self):
        result = runner.invoke(app, ["analyze", "今日はいい天気ですね"])
        assert result.exit_code == 0

    def test_analyze_explain_mode(self):
        result = runner.invoke(app, [
            "analyze", "--explain", "電話番号は090-1234-5678です",
        ])
        assert result.exit_code == 0
        # Explain mode should show the source recognizer
        assert "regex" in result.stdout.lower() or "PHONE_NUMBER" in result.stdout

    def test_analyze_with_input_file(self, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("メールはtanaka@example.comです", encoding="utf-8")

        result = runner.invoke(app, ["analyze", "--input", str(input_file)])

        assert result.exit_code == 0
        assert "EMAIL" in result.stdout


class TestCLIErrors:

    def test_no_command(self):
        result = runner.invoke(app, [])
        # Typer exits with code 2 when no subcommand is given — this is expected
        assert result.exit_code in (0, 2)

    def test_nonexistent_input_file(self):
        result = runner.invoke(app, [
            "anonymize", "--input", "/nonexistent/file.txt",
        ])
        assert result.exit_code != 0
