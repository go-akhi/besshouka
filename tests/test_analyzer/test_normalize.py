"""Tests for the text normalization module."""

from besshouka.analyzer.normalize import normalize_text, clean_punctuation


class TestNormalizeText:
    """Test NFKC normalization."""

    def test_fullwidth_numbers_to_halfwidth(self):
        assert normalize_text("０９０１２３４５６７８") == "09012345678"

    def test_fullwidth_alpha_to_halfwidth(self):
        assert normalize_text("ＡＢＣ") == "ABC"

    def test_fullwidth_mixed_to_halfwidth(self):
        assert normalize_text("ＡＢＣ１２３") == "ABC123"

    def test_halfwidth_katakana_to_fullwidth(self):
        """NFKC converts half-width katakana to full-width."""
        assert normalize_text("ﾀﾅｶ") == "タナカ"

    def test_fullwidth_katakana_preserved(self):
        """Full-width katakana should remain unchanged."""
        assert normalize_text("タナカタロウ") == "タナカタロウ"

    def test_kanji_unchanged(self):
        assert normalize_text("田中太郎") == "田中太郎"

    def test_hiragana_unchanged(self):
        assert normalize_text("たなかたろう") == "たなかたろう"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_pure_ascii(self):
        assert normalize_text("hello world") == "hello world"

    def test_mixed_scripts_with_fullwidth(self):
        """Kanji + full-width numbers should normalize the numbers only."""
        result = normalize_text("電話番号は０９０です")
        assert "090" in result
        assert "電話番号は" in result

    def test_string_length_preserved_for_alphanumeric(self):
        """Full-width → half-width alphanumeric NFKC preserves code point count."""
        original = "０９０"
        normalized = normalize_text(original)
        assert len(original) == len(normalized)


class TestCleanPunctuation:
    """Test Japanese punctuation standardization."""

    def test_fullwidth_hyphen_standardized(self):
        """Full-width hyphen （－） should be standardized."""
        result = clean_punctuation("090－1234－5678")
        assert "－" not in result

    def test_katakana_prolonged_sound_in_phone(self):
        """Katakana prolonged sound mark （ー） used as dash in phone numbers."""
        result = clean_punctuation("090ー1234ー5678")
        assert "ー" not in result

    def test_wave_dash_standardized(self):
        """Wave dash （〜） should be standardized."""
        result = clean_punctuation("090〜1234〜5678")
        assert "〜" not in result

    def test_regular_hyphen_unchanged(self):
        """Standard ASCII hyphen should pass through."""
        assert clean_punctuation("090-1234-5678") == "090-1234-5678"

    def test_empty_string(self):
        assert clean_punctuation("") == ""

    def test_no_punctuation(self):
        text = "田中太郎"
        assert clean_punctuation(text) == text
