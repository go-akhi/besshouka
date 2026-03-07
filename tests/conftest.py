"""Shared fixtures for Besshouka test suite."""

import pytest
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Sample Japanese texts with known PII
# ---------------------------------------------------------------------------

@pytest.fixture
def text_with_person_name():
    """Text containing a person name with honorific and particle."""
    return "田中太郎さんに会いました"


@pytest.fixture
def text_with_phone_mobile():
    """Text containing a mobile phone number with hyphens."""
    return "電話番号は090-1234-5678です"


@pytest.fixture
def text_with_phone_no_hyphens():
    """Text containing a mobile phone number without hyphens."""
    return "電話番号は09012345678です"


@pytest.fixture
def text_with_phone_landline():
    """Text containing a landline phone number."""
    return "電話番号は03-1234-5678です"


@pytest.fixture
def text_with_email():
    """Text containing an email address."""
    return "メールはtanaka@example.comです"


@pytest.fixture
def text_with_my_number():
    """Text containing a My Number (12-digit individual number)."""
    return "マイナンバーは123456789012です"


@pytest.fixture
def text_with_my_number_spaces():
    """Text containing a My Number with spaces."""
    return "マイナンバーは1234 5678 9012です"


@pytest.fixture
def text_with_postal_code():
    """Text containing a Japanese postal code."""
    return "郵便番号は100-0001です"


@pytest.fixture
def text_with_credit_card():
    """Text containing a credit card number."""
    return "カード番号は4111111111111111です"


@pytest.fixture
def text_with_multiple_pii():
    """Text containing multiple PII entities."""
    return "田中太郎さんの電話番号は090-1234-5678で、メールはtanaka@example.comです"


@pytest.fixture
def text_fullwidth_numbers():
    """Text containing full-width numbers."""
    return "電話番号は０９０ー１２３４ー５６７８です"


@pytest.fixture
def text_fullwidth_alpha():
    """Text containing full-width alphabetic characters."""
    return "ＡＢＣメールはＴＡＮＡＫＡ＠ＥＸＡＭＰＬＥ．ＣＯＭです"


@pytest.fixture
def text_no_pii():
    """Text containing no PII."""
    return "今日はいい天気ですね"


@pytest.fixture
def text_empty():
    """Empty text."""
    return ""


@pytest.fixture
def text_ascii_only():
    """Pure ASCII text with no PII."""
    return "Hello world, this is a test."


@pytest.fixture
def text_mixed_scripts():
    """Text mixing kanji, katakana, hiragana, and ASCII."""
    return "株式会社ABCの田中太郎（タナカタロウ）です"


# ---------------------------------------------------------------------------
# Pre-built RecognizerResult-like dicts (used before the class exists)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_recognizer_result_person():
    """A sample result for a detected person name."""
    return {
        "start": 0,
        "end": 4,
        "entity_type": "PERSON",
        "score": 0.85,
        "source": "ginza_ner",
        "text": "田中太郎",
        "recognition_metadata": {},
    }


@pytest.fixture
def sample_recognizer_result_phone():
    """A sample result for a detected phone number."""
    return {
        "start": 5,
        "end": 18,
        "entity_type": "PHONE_NUMBER",
        "score": 1.0,
        "source": "regex_registry",
        "text": "090-1234-5678",
        "recognition_metadata": {},
    }


@pytest.fixture
def sample_recognizer_result_email():
    """A sample result for a detected email address."""
    return {
        "start": 3,
        "end": 23,
        "entity_type": "EMAIL",
        "score": 1.0,
        "source": "regex_registry",
        "text": "tanaka@example.com",
        "recognition_metadata": {},
    }


# ---------------------------------------------------------------------------
# Overlapping results for conflict resolution tests
# ---------------------------------------------------------------------------

@pytest.fixture
def overlapping_results_nested():
    """Two results where one is nested inside the other (longest match wins)."""
    return [
        {
            "start": 0,
            "end": 6,
            "entity_type": "ORGANIZATION",
            "score": 0.80,
            "source": "ginza_ner",
            "text": "山田クリニック",
        },
        {
            "start": 0,
            "end": 2,
            "entity_type": "PERSON",
            "score": 0.90,
            "source": "ginza_ner",
            "text": "山田",
        },
    ]


@pytest.fixture
def overlapping_results_equal_length():
    """Two results with equal length but different scores (score tie-break)."""
    return [
        {
            "start": 0,
            "end": 4,
            "entity_type": "PERSON",
            "score": 0.70,
            "source": "ginza_ner",
            "text": "田中太郎",
        },
        {
            "start": 0,
            "end": 4,
            "entity_type": "ORGANIZATION",
            "score": 0.90,
            "source": "ginza_ner",
            "text": "田中太郎",
        },
    ]


@pytest.fixture
def overlapping_results_structured_vs_unstructured():
    """Regex (structured) vs GiNZA (unstructured) on same span."""
    return [
        {
            "start": 0,
            "end": 12,
            "entity_type": "MY_NUMBER",
            "score": 1.0,
            "source": "regex_registry",
            "text": "123456789012",
        },
        {
            "start": 0,
            "end": 12,
            "entity_type": "NUMBER",
            "score": 0.60,
            "source": "ginza_ner",
            "text": "123456789012",
        },
    ]


@pytest.fixture
def non_overlapping_results():
    """Two results that don't overlap — both should be kept."""
    return [
        {
            "start": 0,
            "end": 4,
            "entity_type": "PERSON",
            "score": 0.85,
            "source": "ginza_ner",
            "text": "田中太郎",
        },
        {
            "start": 10,
            "end": 23,
            "entity_type": "PHONE_NUMBER",
            "score": 1.0,
            "source": "regex_registry",
            "text": "090-1234-5678",
        },
    ]


# ---------------------------------------------------------------------------
# YAML configuration fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def recognizer_yaml_content():
    """Valid recognizer registry YAML content."""
    return textwrap.dedent("""\
        recognizers:
          - name: japanese_phone
            entity_type: PHONE_NUMBER
            pattern: '0\\d{1,4}-?\\d{1,4}-?\\d{4}'
            score: 1.0
            source: regex_registry

          - name: email
            entity_type: EMAIL
            pattern: '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
            score: 1.0
            source: regex_registry

          - name: my_number
            entity_type: MY_NUMBER
            pattern: '\\d{4}\\s?\\d{4}\\s?\\d{4}'
            score: 1.0
            source: regex_registry

          - name: postal_code
            entity_type: POSTAL_CODE
            pattern: '\\d{3}-\\d{4}'
            score: 1.0
            source: regex_registry
    """)


@pytest.fixture
def recognizer_yaml_file(tmp_path, recognizer_yaml_content):
    """Write recognizer YAML to a temp file and return the path."""
    p = tmp_path / "recognizers.yaml"
    p.write_text(recognizer_yaml_content, encoding="utf-8")
    return p


@pytest.fixture
def operator_yaml_content():
    """Valid operator rules YAML content."""
    return textwrap.dedent("""\
        operators:
          PERSON:
            method: replace
            value: "<氏名>"
          PHONE_NUMBER:
            method: mask
            char: "*"
            from_end: 4
          EMAIL:
            method: replace
            value: "<メール>"
          MY_NUMBER:
            method: redact
          CREDIT_CARD:
            method: mask
            char: "*"
            from_end: 4
          LOCATION:
            method: replace
            value: "<住所>"
          ORGANIZATION:
            method: replace
            value: "<組織名>"
    """)


@pytest.fixture
def operator_yaml_file(tmp_path, operator_yaml_content):
    """Write operator YAML to a temp file and return the path."""
    p = tmp_path / "operators.yaml"
    p.write_text(operator_yaml_content, encoding="utf-8")
    return p


@pytest.fixture
def invalid_yaml_content():
    """Malformed YAML content."""
    return "recognizers:\n  - name: broken\n    pattern: '[unterminated"


@pytest.fixture
def invalid_yaml_file(tmp_path, invalid_yaml_content):
    """Write invalid YAML to a temp file and return the path."""
    p = tmp_path / "invalid.yaml"
    p.write_text(invalid_yaml_content, encoding="utf-8")
    return p


@pytest.fixture
def missing_fields_yaml_content():
    """YAML with missing required fields."""
    return textwrap.dedent("""\
        recognizers:
          - name: incomplete
            entity_type: PHONE_NUMBER
    """)


@pytest.fixture
def missing_fields_yaml_file(tmp_path, missing_fields_yaml_content):
    """Write YAML with missing fields to a temp file and return the path."""
    p = tmp_path / "missing_fields.yaml"
    p.write_text(missing_fields_yaml_content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Custom operator function (for testing custom.py operator)
# ---------------------------------------------------------------------------

def sample_custom_function(text: str, params: dict) -> str:
    """A sample custom operator function that reverses the text."""
    return text[::-1]


def sample_custom_function_with_params(text: str, params: dict) -> str:
    """A sample custom operator function that uses params."""
    prefix = params.get("prefix", "")
    suffix = params.get("suffix", "")
    return f"{prefix}{text}{suffix}"
