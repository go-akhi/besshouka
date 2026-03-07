"""Tests for the GiNZA NER recognizer.

These tests require GiNZA and ja-ginza to be installed.
They are marked as slow because model loading takes time.
"""

import pytest

from besshouka.analyzer.recognizers.ginza_recognizer import GinzaRecognizer


@pytest.mark.slow
class TestGinzaPersonDetection:
    """Test person name detection via GiNZA."""

    def setup_method(self):
        self.recognizer = GinzaRecognizer()

    def test_detect_person_name(self):
        results = self.recognizer.recognize("田中太郎さんに会いました")
        person_results = [r for r in results if r.entity_type == "PERSON"]
        assert len(person_results) >= 1
        assert any(r.text == "田中太郎" for r in person_results)

    def test_detect_person_score_is_probabilistic(self):
        results = self.recognizer.recognize("田中太郎さんに会いました")
        person_results = [r for r in results if r.entity_type == "PERSON"]
        if person_results:
            assert 0.0 < person_results[0].score <= 1.0

    def test_correct_offsets_for_person(self):
        text = "田中太郎さんに会いました"
        results = self.recognizer.recognize(text)
        for r in results:
            assert text[r.start:r.end] == r.text


@pytest.mark.slow
class TestGinzaOrganizationDetection:
    """Test organization name detection via GiNZA."""

    def setup_method(self):
        self.recognizer = GinzaRecognizer()

    def test_detect_organization(self):
        results = self.recognizer.recognize("株式会社トヨタ自動車の発表によると")
        org_results = [r for r in results if r.entity_type == "ORGANIZATION"]
        assert len(org_results) >= 1


@pytest.mark.slow
class TestGinzaLocationDetection:
    """Test location detection via GiNZA."""

    def setup_method(self):
        self.recognizer = GinzaRecognizer()

    def test_detect_location(self):
        results = self.recognizer.recognize("東京都渋谷区に住んでいます")
        location_results = [r for r in results if r.entity_type == "LOCATION"]
        assert len(location_results) >= 1


@pytest.mark.slow
class TestGinzaLabelMapping:
    """Test that GiNZA labels are mapped to standardized entity types."""

    def setup_method(self):
        self.recognizer = GinzaRecognizer()

    def test_all_results_have_standardized_types(self):
        """All entity_type values should be from the standardized taxonomy."""
        text = "田中太郎は東京都で株式会社ABCに勤めています"
        results = self.recognizer.recognize(text)
        valid_types = {"PERSON", "LOCATION", "ORGANIZATION", "DATE", "TIME", "MONEY", "PERCENT", "QUANTITY"}
        for r in results:
            assert r.entity_type in valid_types, f"Unexpected entity type: {r.entity_type}"

    def test_source_is_ginza(self):
        results = self.recognizer.recognize("田中太郎さん")
        for r in results:
            assert r.source == "ginza_ner"


@pytest.mark.slow
class TestGinzaNoEntities:
    """Test behavior when no entities are found."""

    def setup_method(self):
        self.recognizer = GinzaRecognizer()

    def test_no_entities_in_plain_text(self):
        results = self.recognizer.recognize("今日はいい天気ですね")
        # GiNZA might or might not find entities here; just check it doesn't crash
        assert isinstance(results, list)

    def test_empty_string(self):
        results = self.recognizer.recognize("")
        assert results == []


class TestGinzaModelUnavailable:
    """Test graceful handling when GiNZA model is not available."""

    def test_recognizer_creation_without_model(self, monkeypatch):
        """If the model can't be loaded, recognize() should return empty list or raise clearly."""
        # This test verifies the behavior contract — implementation may vary
        recognizer = GinzaRecognizer()
        # Force model loading to fail
        monkeypatch.setattr(
            recognizer, "_load_model",
            lambda: (_ for _ in ()).throw(OSError("Model not found")),
        )
        # Should either return empty results or raise a clear error
        try:
            results = recognizer.recognize("田中太郎")
            assert results == []
        except OSError:
            pass  # Also acceptable — clear error propagation
