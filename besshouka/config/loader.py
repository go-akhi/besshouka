"""YAML configuration loader and validator for recognizer and operator configs."""

from pathlib import Path

import yaml


_REQUIRED_RECOGNIZER_FIELDS = {"name", "entity_type", "pattern", "score"}


def load_recognizer_config(path: Path) -> dict:
    """Load and validate a recognizer registry YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed config dict with a 'recognizers' key.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is malformed or entries are missing required fields.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Recognizer config not found: {path}")

    with open(path, encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Malformed YAML in {path}: {e}") from e

    if not isinstance(config, dict) or "recognizers" not in config:
        raise ValueError(f"Recognizer config must contain a 'recognizers' key: {path}")

    for i, entry in enumerate(config["recognizers"]):
        missing = _REQUIRED_RECOGNIZER_FIELDS - set(entry.keys())
        if missing:
            raise ValueError(
                f"Recognizer entry {i} ('{entry.get('name', '?')}') "
                f"is missing required fields: {missing}"
            )

    return config


def load_operator_config(path: Path) -> dict:
    """Load and validate an operator rules YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed config dict with an 'operators' key.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is malformed or entries are missing 'method'.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Operator config not found: {path}")

    with open(path, encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Malformed YAML in {path}: {e}") from e

    if not isinstance(config, dict) or "operators" not in config:
        raise ValueError(f"Operator config must contain an 'operators' key: {path}")

    for entity_type, op_config in config["operators"].items():
        if "method" not in op_config:
            raise ValueError(
                f"Operator config for '{entity_type}' is missing required 'method' field"
            )

    return config
