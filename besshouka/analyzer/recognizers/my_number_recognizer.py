"""Dedicated recognizer for Japanese My Number (マイナンバー).

Matches 12-digit numbers (with optional dashes, spaces, or newlines),
validates the check digit using the official mod-11 algorithm, and
assigns confidence based on context:

- Valid check digit only → low confidence (0.4)
- Valid check digit + nearby context keyword → high confidence (1.0)

The pipeline's score threshold controls whether low-confidence matches
are anonymized or silently dropped.
"""

import re

from besshouka.analyzer.recognizers.base import BaseRecognizer
from besshouka.models.recognizer_result import RecognizerResult

_MY_NUMBER_PATTERN = re.compile(r"\d{4}[\s\n-]*\d{4}[\s\n-]*\d{4}")

# Context keywords that appear near My Number values
_CONTEXT_KEYWORDS = [
    "マイナンバー",
    "マイナンバ",
    "個人番号",
    "My Number",
    "通知カード",
    "番号確認",
    "番号通知",
    "個人番号カード",
    "マイナカード",
    "マイナ保険証",
    "社会保障",
    "税番号",
]

# Max characters between keyword and number to consider them related
_CONTEXT_WINDOW = 10

# Confidence scores
_SCORE_WITH_CONTEXT = 1.0
_SCORE_WITHOUT_CONTEXT = 0.4

# Weights for the check digit calculation (positions 1-11, left to right)
_WEIGHTS = [6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def _valid_check_digit(digits: str) -> bool:
    """Validate the My Number check digit (12th digit) using mod-11.

    Args:
        digits: A string of exactly 12 digit characters (no separators).

    Returns:
        True if the check digit is valid.
    """
    if len(digits) != 12 or not digits.isdigit():
        return False

    q = sum(int(digits[i]) * _WEIGHTS[i] for i in range(11))
    remainder = q % 11

    expected = 0 if remainder <= 1 else 11 - remainder
    return int(digits[11]) == expected


class MyNumberRecognizer(BaseRecognizer):
    """Recognizer for Japanese Individual Number (マイナンバー).

    Always emits a result for valid check digits. Score depends on
    whether a context keyword is found nearby:
    - With context: 1.0
    - Without context: 0.4

    The pipeline's score_threshold determines whether low-confidence
    matches are anonymized.
    """

    @property
    def name(self) -> str:
        return "my_number"

    @property
    def source(self) -> str:
        return "my_number"

    def _has_context_keyword(self, text: str, number_start: int, number_end: int) -> bool:
        """Check if a context keyword appears near the number.

        Searches both before and after the number within the context window.
        """
        max_kw_len = max(len(k) for k in _CONTEXT_KEYWORDS)

        # Search before the number
        before_start = max(0, number_start - max_kw_len - _CONTEXT_WINDOW)
        before_window = text[before_start:number_start]

        for keyword in _CONTEXT_KEYWORDS:
            idx = before_window.rfind(keyword)
            if idx == -1:
                continue
            kw_end = before_start + idx + len(keyword)
            if number_start - kw_end <= _CONTEXT_WINDOW:
                return True

        # Search after the number
        after_end = min(len(text), number_end + max_kw_len + _CONTEXT_WINDOW)
        after_window = text[number_end:after_end]

        for keyword in _CONTEXT_KEYWORDS:
            idx = after_window.find(keyword)
            if idx == -1:
                continue
            if idx <= _CONTEXT_WINDOW:
                return True

        return False

    def recognize(self, text: str) -> list[RecognizerResult]:
        """Find and validate My Number patterns in text.

        Emits all matches with valid check digits. Score is 1.0 when
        a context keyword is nearby, 0.4 otherwise.
        """
        results = []
        for match in _MY_NUMBER_PATTERN.finditer(text):
            digits = re.sub(r"[\s\n-]", "", match.group())
            if not _valid_check_digit(digits):
                continue

            has_context = self._has_context_keyword(text, match.start(), match.end())

            results.append(
                RecognizerResult(
                    start=match.start(),
                    end=match.end(),
                    entity_type="MY_NUMBER",
                    score=_SCORE_WITH_CONTEXT if has_context else _SCORE_WITHOUT_CONTEXT,
                    source="my_number",
                    text=match.group(),
                )
            )

        return results
