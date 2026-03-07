# Config — Configuration Loading

Loads and validates the two YAML configuration files that drive Besshouka: the recognizer registry and the operator rules.

## Functions

### `load_recognizer_config(path) -> dict`

Loads a recognizer registry YAML file. Each entry must have:

| Field         | Required | Description                          |
|---------------|----------|--------------------------------------|
| `name`        | Yes      | Unique recognizer name               |
| `entity_type` | Yes      | Standardized entity type             |
| `pattern`     | Yes      | Regex pattern string                 |
| `score`       | Yes      | Confidence score (typically `1.0`)   |
| `source`      | No       | Defaults to `regex_registry`         |

Raises `FileNotFoundError` if the file doesn't exist, `ValueError` if the YAML is malformed or entries are missing required fields.

### `load_operator_config(path) -> dict`

Loads an operator rules YAML file. Each entity type entry must have a `method` field.

Raises `FileNotFoundError` if the file doesn't exist, `ValueError` if the YAML is malformed or `method` is missing.

## Pointing the Engine at Custom Config Files

### Via CLI

```bash
python -m besshouka.cli anonymize --recognizers my_patterns.yaml --rules my_operators.yaml "text"
```

### Programmatically

```python
from besshouka.config.loader import load_recognizer_config, load_operator_config

rec_config = load_recognizer_config("my_patterns.yaml")
op_config = load_operator_config("my_operators.yaml")
```

If no custom files are provided, the CLI defaults to `besshouka/defaults/recognizers.yaml` and `besshouka/defaults/operators.yaml`.
