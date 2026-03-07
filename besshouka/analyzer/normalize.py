"""Text normalization for Japanese input before PII recognition."""

import unicodedata


# Mapping of Japanese dash-like characters to standard ASCII hyphen
_DASH_MAP = str.maketrans({
    "\uFF0D": "-",  # － Full-width hyphen-minus
    "\u30FC": "-",  # ー Katakana prolonged sound mark
    "\u301C": "-",  # 〜 Wave dash
    "\uFF5E": "-",  # ～ Full-width tilde
    "\u2012": "-",  # ‒ Figure dash
    "\u2013": "-",  # – En dash
    "\u2014": "-",  # — Em dash
    "\u2015": "-",  # ― Horizontal bar
})


def normalize_text(text: str) -> str:
    """Apply NFKC normalization to text.

    Converts full-width alphanumeric characters to half-width (e.g. ０９０ → 090).
    Converts half-width katakana to full-width.
    Leaves kanji and full-width katakana unchanged.
    """
    return unicodedata.normalize("NFKC", text)


def clean_punctuation(text: str) -> str:
    """Standardize Japanese dash-like characters to ASCII hyphen.

    Handles full-width hyphens, katakana prolonged sound marks,
    wave dashes, and other dash variants commonly used in phone numbers
    and other formatted data.
    """
    return text.translate(_DASH_MAP)
