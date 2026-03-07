"""Tests for the ProcessingContext data object."""

from besshouka.orchestrator.context import ProcessingContext


class TestProcessingContextCreation:

    def test_create_with_text(self):
        ctx = ProcessingContext(original_text="田中太郎さんに会いました")
        assert ctx.original_text == "田中太郎さんに会いました"

    def test_working_text_initially_none(self):
        ctx = ProcessingContext(original_text="test")
        assert ctx.working_text is None

    def test_recognizer_results_initially_empty(self):
        ctx = ProcessingContext(original_text="test")
        assert ctx.recognizer_results == []

    def test_engine_result_initially_none(self):
        ctx = ProcessingContext(original_text="test")
        assert ctx.engine_result is None

    def test_metadata_default_empty_dict(self):
        ctx = ProcessingContext(original_text="test")
        assert ctx.metadata == {}

    def test_metadata_custom(self):
        ctx = ProcessingContext(
            original_text="test",
            metadata={"filename": "input.txt", "timestamp": "2026-03-07"},
        )
        assert ctx.metadata["filename"] == "input.txt"

    def test_original_text_preserved(self):
        """original_text should remain unchanged throughout processing."""
        ctx = ProcessingContext(original_text="田中太郎さんに会いました")
        ctx.working_text = "normalized version"
        assert ctx.original_text == "田中太郎さんに会いました"
