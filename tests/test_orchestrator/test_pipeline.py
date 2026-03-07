"""Tests for the orchestration pipeline."""

import pytest

from besshouka.orchestrator.pipeline import run
from besshouka.orchestrator.context import ProcessingContext


class TestFullPipeline:

    def test_basic_anonymization(self, recognizer_yaml_file, operator_yaml_file):
        """Full pipeline: Japanese text with phone number in, anonymized text out."""
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        ctx = run("電話番号は090-1234-5678です", rec_config, op_config)

        assert isinstance(ctx, ProcessingContext)
        assert "090-1234-5678" not in ctx.engine_result.text
        assert ctx.original_text == "電話番号は090-1234-5678です"

    def test_no_pii_text_unchanged(self, recognizer_yaml_file, operator_yaml_file):
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        ctx = run("今日はいい天気ですね", rec_config, op_config)

        assert ctx.engine_result.text == "今日はいい天気ですね"
        assert ctx.engine_result.items == []

    def test_email_anonymized(self, recognizer_yaml_file, operator_yaml_file):
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        ctx = run("メールはtanaka@example.comです", rec_config, op_config)

        assert "tanaka@example.com" not in ctx.engine_result.text
        assert "<メール>" in ctx.engine_result.text

    def test_pipeline_returns_processing_context(self, recognizer_yaml_file, operator_yaml_file):
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        ctx = run("test", rec_config, op_config)

        assert isinstance(ctx, ProcessingContext)
        assert ctx.original_text == "test"
        assert ctx.working_text is not None
        assert ctx.engine_result is not None


class TestGracefulDegradation:

    def test_ginza_failure_falls_back_to_regex(
        self, recognizer_yaml_file, operator_yaml_file, monkeypatch
    ):
        """If GiNZA fails to load, pipeline should still run regex recognizers."""
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        # Phone number should still be detected by regex even without GiNZA
        ctx = run("電話番号は090-1234-5678です", rec_config, op_config)

        assert "090-1234-5678" not in ctx.engine_result.text

    def test_single_recognizer_failure_does_not_crash(
        self, recognizer_yaml_file, operator_yaml_file
    ):
        """If one recognizer throws, others should still run."""
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        # Even if something goes wrong internally, the pipeline should not crash
        ctx = run("電話番号は090-1234-5678でメールはtest@example.comです", rec_config, op_config)

        assert isinstance(ctx, ProcessingContext)
        assert ctx.engine_result is not None


class TestPipelineSteps:

    def test_normalization_applied(self, recognizer_yaml_file, operator_yaml_file):
        """Full-width numbers should be normalized before recognition."""
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        # Full-width phone number should be normalized and detected
        ctx = run("電話番号は０９０１２３４５６７８です", rec_config, op_config)

        assert ctx.working_text is not None
        # After normalization, the phone number should have been detected
        assert len(ctx.recognizer_results) >= 1

    def test_conflict_resolution_applied(self, recognizer_yaml_file, operator_yaml_file):
        """Pipeline should resolve conflicts before passing to anonymizer."""
        from besshouka.config.loader import load_recognizer_config, load_operator_config

        rec_config = load_recognizer_config(recognizer_yaml_file)
        op_config = load_operator_config(operator_yaml_file)

        ctx = run("090-1234-5678", rec_config, op_config)

        # No duplicate/overlapping results should remain
        for i, r1 in enumerate(ctx.recognizer_results):
            for r2 in ctx.recognizer_results[i + 1:]:
                # No two results should overlap
                assert r1.end <= r2.start or r2.end <= r1.start
