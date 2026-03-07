"""Recognizer registry \u2014 loads recognizers from YAML and holds them in memory."""

from pathlib import Path

from besshouka.analyzer.recognizers.base import BaseRecognizer
from besshouka.analyzer.recognizers.regex_recognizer import RegexRecognizer
from besshouka.config.loader import load_recognizer_config


_registry: list[BaseRecognizer] = []


def load_recognizers(path: Path) -> list[BaseRecognizer]:
    """Parse a recognizer YAML file and instantiate one RegexRecognizer per entry.

    Clears any previously loaded recognizers and replaces with the new set.

    Args:
        path: Path to the recognizer registry YAML file.

    Returns:
        List of instantiated recognizers.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValueError: If entries are missing required fields.
    """
    global _registry

    config = load_recognizer_config(path)

    recognizers = []
    for entry in config["recognizers"]:
        recognizers.append(
            RegexRecognizer(
                name=entry["name"],
                entity_type=entry["entity_type"],
                pattern=entry["pattern"],
                score=entry["score"],
                source=entry.get("source", "regex_registry"),
            )
        )

    _registry = recognizers
    return recognizers


def get_all_recognizers() -> list[BaseRecognizer]:
    """Return all currently loaded recognizers (regex + any others)."""
    return list(_registry)
