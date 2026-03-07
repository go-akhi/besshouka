"""Tests for the RegexRecognizer class."""

from besshouka.analyzer.recognizers.regex_recognizer import RegexRecognizer


class TestPhoneNumberDetection:
    """Test phone number regex matching."""

    def setup_method(self):
        self.recognizer = RegexRecognizer(
            name="japanese_phone",
            entity_type="PHONE_NUMBER",
            pattern=r"0\d{1,4}-?\d{1,4}-?\d{4}",
            score=1.0,
            source="regex_registry",
        )

    def test_mobile_with_hyphens(self):
        results = self.recognizer.recognize("電話番号は090-1234-5678です")
        assert len(results) == 1
        assert results[0].text == "090-1234-5678"
        assert results[0].entity_type == "PHONE_NUMBER"

    def test_mobile_without_hyphens(self):
        results = self.recognizer.recognize("電話番号は09012345678です")
        assert len(results) == 1
        assert results[0].text == "09012345678"

    def test_landline(self):
        results = self.recognizer.recognize("電話番号は03-1234-5678です")
        assert len(results) == 1
        assert results[0].text == "03-1234-5678"

    def test_no_match(self):
        results = self.recognizer.recognize("今日はいい天気ですね")
        assert len(results) == 0

    def test_multiple_matches(self):
        text = "090-1234-5678と03-9876-5432に電話してください"
        results = self.recognizer.recognize(text)
        assert len(results) == 2

    def test_score_always_one(self):
        results = self.recognizer.recognize("090-1234-5678")
        assert all(r.score == 1.0 for r in results)

    def test_correct_offsets(self):
        text = "電話番号は090-1234-5678です"
        results = self.recognizer.recognize(text)
        assert len(results) == 1
        assert text[results[0].start:results[0].end] == "090-1234-5678"


class TestEmailDetection:
    """Test email regex matching."""

    def setup_method(self):
        self.recognizer = RegexRecognizer(
            name="email",
            entity_type="EMAIL",
            pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            score=1.0,
            source="regex_registry",
        )

    def test_standard_email(self):
        results = self.recognizer.recognize("メールはtanaka@example.comです")
        assert len(results) == 1
        assert results[0].text == "tanaka@example.com"
        assert results[0].entity_type == "EMAIL"

    def test_email_with_dots(self):
        results = self.recognizer.recognize("first.last@company.co.jp")
        assert len(results) == 1
        assert results[0].text == "first.last@company.co.jp"

    def test_no_email(self):
        results = self.recognizer.recognize("田中太郎さんに会いました")
        assert len(results) == 0

    def test_correct_offsets(self):
        text = "メールはtanaka@example.comです"
        results = self.recognizer.recognize(text)
        assert text[results[0].start:results[0].end] == "tanaka@example.com"


class TestMyNumberDetection:
    """Test My Number (マイナンバー) regex matching."""

    def setup_method(self):
        self.recognizer = RegexRecognizer(
            name="my_number",
            entity_type="MY_NUMBER",
            pattern=r"\d{4}\s?\d{4}\s?\d{4}",
            score=1.0,
            source="regex_registry",
        )

    def test_my_number_no_spaces(self):
        results = self.recognizer.recognize("マイナンバーは123456789012です")
        assert len(results) == 1
        assert results[0].text == "123456789012"

    def test_my_number_with_spaces(self):
        results = self.recognizer.recognize("マイナンバーは1234 5678 9012です")
        assert len(results) == 1
        assert results[0].text == "1234 5678 9012"

    def test_no_match(self):
        results = self.recognizer.recognize("今日は2024年3月7日です")
        assert len(results) == 0


class TestPostalCodeDetection:
    """Test postal code regex matching."""

    def setup_method(self):
        self.recognizer = RegexRecognizer(
            name="postal_code",
            entity_type="POSTAL_CODE",
            pattern=r"\d{3}-\d{4}",
            score=1.0,
            source="regex_registry",
        )

    def test_postal_code(self):
        results = self.recognizer.recognize("郵便番号は100-0001です")
        assert len(results) == 1
        assert results[0].text == "100-0001"
        assert results[0].entity_type == "POSTAL_CODE"

    def test_no_match(self):
        results = self.recognizer.recognize("番号は12345です")
        assert len(results) == 0


class TestRegexRecognizerProperties:
    """Test recognizer metadata properties."""

    def test_name(self):
        r = RegexRecognizer(
            name="test_recognizer", entity_type="TEST",
            pattern=r"\d+", score=1.0, source="regex_registry",
        )
        assert r.name == "test_recognizer"

    def test_source(self):
        r = RegexRecognizer(
            name="test", entity_type="TEST",
            pattern=r"\d+", score=1.0, source="custom",
        )
        assert r.source == "custom"

    def test_entity_type(self):
        r = RegexRecognizer(
            name="test", entity_type="PHONE_NUMBER",
            pattern=r"\d+", score=1.0, source="regex_registry",
        )
        assert r.entity_type == "PHONE_NUMBER"
