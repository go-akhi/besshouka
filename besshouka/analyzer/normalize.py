"""Text normalization for Japanese input before PII recognition."""

import re
import unicodedata


# Mapping of Japanese dash-like characters to standard ASCII hyphen.
# Note: ー (U+30FC katakana prolonged sound mark) is NOT included here
# because it is a valid katakana character (e.g. マイナンバー). It is only
# converted to a hyphen when it appears between digits (see clean_punctuation).
_DASH_MAP = str.maketrans({
    "\uFF0D": "-",  # － Full-width hyphen-minus
    "\u301C": "-",  # 〜 Wave dash
    "\uFF5E": "-",  # ～ Full-width tilde
    "\u2012": "-",  # ‒ Figure dash
    "\u2013": "-",  # – En dash
    "\u2014": "-",  # — Em dash
    "\u2015": "-",  # ― Horizontal bar
})

# Katakana prolonged sound mark used as a digit separator (e.g. ０９０ー１２３４ー５６７８)
_KANA_DASH_BETWEEN_DIGITS = re.compile(r"(?<=\d)\u30FC(?=\d)")


def normalize_text(text: str) -> str:
    """Apply NFKC normalization to text.

    Converts full-width alphanumeric characters to half-width (e.g. ０９０ → 090).
    Converts half-width katakana to full-width.
    Leaves kanji and full-width katakana unchanged.
    """
    return unicodedata.normalize("NFKC", text)


def clean_punctuation(text: str) -> str:
    """Standardize Japanese dash-like characters to ASCII hyphen.

    Handles full-width hyphens, wave dashes, and other dash variants
    commonly used in phone numbers and other formatted data.

    The katakana prolonged sound mark (ー) is only converted when it
    appears between digits, preserving it in normal Japanese text
    (e.g. マイナンバー).
    """
    text = text.translate(_DASH_MAP)
    text = _KANA_DASH_BETWEEN_DIGITS.sub("-", text)
    return text
