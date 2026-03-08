"""Tests for the MyNumberRecognizer class."""

from besshouka.analyzer.recognizers.my_number_recognizer import (
    MyNumberRecognizer,
    _valid_check_digit,
)


class TestCheckDigitValidation:
    """Test the mod-11 check digit algorithm."""

    def test_valid_check_digit(self):
        assert _valid_check_digit("123456789018") is True

    def test_invalid_check_digit(self):
        assert _valid_check_digit("123456789012") is False

    def test_all_zeros_except_check(self):
        # 00000000000 → Q=0, R=0, check=0
        assert _valid_check_digit("000000000000") is True

    def test_too_short(self):
        assert _valid_check_digit("12345678901") is False

    def test_too_long(self):
        assert _valid_check_digit("1234567890123") is False

    def test_non_digits(self):
        assert _valid_check_digit("12345678901a") is False

    def test_with_separators_rejected(self):
        # Raw function expects digits only
        assert _valid_check_digit("1234-5678-9018") is False


class TestMyNumberRecognition:
    """Test MyNumberRecognizer pattern matching + check digit + context."""

    def setup_method(self):
        self.recognizer = MyNumberRecognizer()

    def test_valid_with_context(self):
        results = self.recognizer.recognize("マイナンバーは123456789018です")
        assert len(results) == 1
        assert results[0].text == "123456789018"
        assert results[0].entity_type == "MY_NUMBER"
        assert results[0].score == 1.0

    def test_valid_with_spaces_and_context(self):
        results = self.recognizer.recognize("マイナンバーは1234 5678 9018です")
        assert len(results) == 1
        assert results[0].text == "1234 5678 9018"

    def test_valid_with_dashes_and_context(self):
        results = self.recognizer.recognize("マイナンバーは1234-5678-9018です")
        assert len(results) == 1
        assert results[0].text == "1234-5678-9018"

    def test_valid_with_multiple_spaces_and_context(self):
        results = self.recognizer.recognize("マイナンバーは1234  5678 9018です")
        assert len(results) == 1
        assert results[0].score == 1.0

    def test_valid_with_newline_and_context(self):
        results = self.recognizer.recognize("マイナンバーは1234\n5678\n9018です")
        assert len(results) == 1
        assert results[0].score == 1.0

    def test_multiple_spaces_no_context_low_confidence(self):
        results = self.recognizer.recognize("1234  5678 9018")
        assert len(results) == 1
        assert results[0].score == 0.4

    def test_no_context_low_confidence(self):
        """Valid check digit but no context keyword — low confidence."""
        results = self.recognizer.recognize("番号は123456789018です")
        assert len(results) == 1
        assert results[0].score == 0.4

    def test_bare_number_low_confidence(self):
        """Bare valid number without any surrounding text — low confidence."""
        results = self.recognizer.recognize("123456789018")
        assert len(results) == 1
        assert results[0].score == 0.4

    def test_invalid_check_digit_rejected(self):
        results = self.recognizer.recognize("マイナンバーは123456789012です")
        assert len(results) == 0

    def test_invalid_check_digit_with_dashes_rejected(self):
        results = self.recognizer.recognize("マイナンバーは1234-5678-9012です")
        assert len(results) == 0

    def test_correct_offsets(self):
        text = "マイナンバーは123456789018です"
        results = self.recognizer.recognize(text)
        assert len(results) == 1
        assert text[results[0].start:results[0].end] == "123456789018"

    def test_correct_offsets_with_dashes(self):
        text = "マイナンバーは1234-5678-9018です"
        results = self.recognizer.recognize(text)
        assert len(results) == 1
        assert text[results[0].start:results[0].end] == "1234-5678-9018"

    def test_no_match_in_plain_text(self):
        results = self.recognizer.recognize("今日はいい天気ですね")
        assert len(results) == 0

    def test_empty_text(self):
        results = self.recognizer.recognize("")
        assert len(results) == 0

    def test_properties(self):
        assert self.recognizer.name == "my_number"
        assert self.recognizer.source == "my_number"


class TestContextKeywords:
    """Test various context keywords trigger recognition."""

    def setup_method(self):
        self.recognizer = MyNumberRecognizer()

    def test_mainanbaa(self):
        results = self.recognizer.recognize("マイナンバー：123456789018")
        assert len(results) == 1

    def test_kojin_bangou(self):
        results = self.recognizer.recognize("個人番号：123456789018")
        assert len(results) == 1

    def test_mainanbaa_short_form(self):
        results = self.recognizer.recognize("マイナンバ：123456789018")
        assert len(results) == 1

    def test_my_number_english(self):
        results = self.recognizer.recognize("My Number：123456789018")
        assert len(results) == 1

    def test_tsuchi_card(self):
        results = self.recognizer.recognize("通知カード：123456789018")
        assert len(results) == 1

    def test_bangou_kakunin(self):
        results = self.recognizer.recognize("番号確認：123456789018")
        assert len(results) == 1

    def test_kojin_bangou_card(self):
        results = self.recognizer.recognize("個人番号カード：123456789018")
        assert len(results) == 1

    def test_maina_card(self):
        results = self.recognizer.recognize("マイナカード：123456789018")
        assert len(results) == 1

    def test_maina_hoken(self):
        results = self.recognizer.recognize("マイナ保険証：123456789018")
        assert len(results) == 1

    def test_shakai_hoshou(self):
        results = self.recognizer.recognize("社会保障：123456789018")
        assert len(results) == 1

    def test_zei_bangou(self):
        results = self.recognizer.recognize("税番号：123456789018")
        assert len(results) == 1

    def test_keyword_after_number(self):
        """Context keyword appearing after the number also works."""
        results = self.recognizer.recognize("123456789018がマイナンバーです")
        assert len(results) == 1

    def test_keyword_with_gap(self):
        """Keyword within 10 chars of number is accepted."""
        results = self.recognizer.recognize("マイナンバーの番号は123456789018です")
        assert len(results) == 1

    def test_keyword_too_far_before(self):
        """Keyword more than 10 chars before number — low confidence."""
        results = self.recognizer.recognize("マイナンバーですが、それはまた別の話で、番号は123456789018です")
        assert len(results) == 1
        assert results[0].score == 0.4

    def test_keyword_too_far_after(self):
        """Keyword more than 10 chars after number — low confidence."""
        results = self.recognizer.recognize("123456789018ですが、それはまた別の話で、マイナンバーです")
        assert len(results) == 1
        assert results[0].score == 0.4

    def test_only_number_result_emitted(self):
        """Only the number is emitted, never the keyword."""
        results = self.recognizer.recognize("マイナンバー：123456789018")
        assert len(results) == 1
        assert results[0].text == "123456789018"
