# Models — Data Contracts

Shared data structures used across the analyzer, anonymizer, and orchestrator. This module contains no business logic — only dataclass definitions.

These exist as a separate module to avoid circular imports between analyzer and anonymizer.

## RecognizerResult

Returned by every recognizer to describe a detected PII span.

```python
from besshouka.models.recognizer_result import RecognizerResult
```

| Field                  | Type   | Description                              |
|------------------------|--------|------------------------------------------|
| `start`                | `int`  | Character offset — start of PII          |
| `end`                  | `int`  | Character offset — end of PII            |
| `entity_type`          | `str`  | Standardized category (e.g. `PERSON`)    |
| `score`                | `float`| Confidence (0.0–1.0)                     |
| `source`               | `str`  | Which recognizer produced this result    |
| `text`                 | `str`  | The matched snippet                      |
| `recognition_metadata` | `dict` | Optional extra info (default: `{}`)      |

The `text` field should always equal `original_text[start:end]`.

## OperatorResult

Audit trail entry for a single anonymization operation.

```python
from besshouka.models.engine_result import OperatorResult
```

| Field           | Type   | Description                               |
|-----------------|--------|-------------------------------------------|
| `entity_type`   | `str`  | PII category that was anonymized          |
| `start`         | `int`  | New index in the **anonymized** string    |
| `end`           | `int`  | New index in the **anonymized** string    |
| `operator`      | `str`  | Which operator was applied                |
| `original_text` | `str`  | The original PII snippet                  |

Note: `start`/`end` refer to positions in the output string, not the input.

## EngineResult

Output of the anonymization engine.

```python
from besshouka.models.engine_result import EngineResult
```

| Field   | Type                 | Description                    |
|---------|----------------------|--------------------------------|
| `text`  | `str`                | Fully anonymized string        |
| `items` | `list[OperatorResult]`| Audit trail of every change   |
