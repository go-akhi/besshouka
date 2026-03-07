# Recognizers — Detection Plugins

Each recognizer scans normalized text and returns a list of `RecognizerResult` objects. All recognizers subclass `BaseRecognizer`.

## The BaseRecognizer Contract

```python
class BaseRecognizer(ABC):
    @property
    def name(self) -> str: ...
    @property
    def source(self) -> str: ...
    def recognize(self, text: str) -> list[RecognizerResult]: ...
```

- `name` — unique identifier for this recognizer.
- `source` — category identifier (e.g. `regex_registry`, `ginza_ner`, `custom`).
- `recognize(text)` — scan the text and return all detected PII spans.

Each `RecognizerResult` must have: `start`, `end`, `entity_type`, `score`, `source`, `text`.

## Built-in Recognizers

### RegexRecognizer (`regex_recognizer.py`)

A single generic class, instantiated once per entry in the YAML recognizer registry. Not one class per pattern — one class, many instances.

Each instance carries: `name`, `entity_type`, `pattern` (compiled regex), `score`, `source`.

Score is always `1.0` for regex recognizers — matches are deterministic.

### GinzaRecognizer (`ginza_recognizer.py`)

Wraps GiNZA/spaCy for Japanese NER. The spaCy model is lazy-loaded on first call to `recognize()`.

GiNZA labels are mapped to the standardized entity types via an internal label map. Unmapped labels are skipped with a debug log.

Score is probabilistic — reflects the model's confidence.

## How to Write Your Own Recognizer

1. Create a new `.py` file in this directory.
2. Subclass `BaseRecognizer`:

```python
from besshouka.analyzer.recognizers.base import BaseRecognizer
from besshouka.models.recognizer_result import RecognizerResult


class MyRecognizer(BaseRecognizer):

    @property
    def name(self) -> str:
        return "my_recognizer"

    @property
    def source(self) -> str:
        return "custom"

    def recognize(self, text: str) -> list[RecognizerResult]:
        results = []
        # Your detection logic here
        # For each match, append:
        #   RecognizerResult(start=..., end=..., entity_type="...",
        #                    score=..., source=self.source, text=...)
        return results
```

3. Register it in the pipeline. In `orchestrator/pipeline.py`, import your recognizer and add it to the recognizers list alongside the regex and GiNZA recognizers.

## Score Conventions

| Source          | Score    | Rationale                    |
|-----------------|----------|------------------------------|
| `regex_registry`| `1.0`    | Deterministic — it matched   |
| `ginza_ner`     | `0.0–1.0`| Model confidence             |
| `custom`        | Your call| Developer's judgement        |

## Conflict Resolution

When multiple recognizers detect overlapping spans, the conflict resolver picks a winner:

1. **Longest match wins** — if one span contains another, the longer one is kept.
2. **Score tie-breaker** — if spans are equal length, the higher score wins.
3. **Structured > unstructured** — regex (deterministic) wins over GiNZA (probabilistic) at equal length and score.
