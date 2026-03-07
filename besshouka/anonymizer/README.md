# Anonymizer — Transformation Pipeline

The anonymizer takes text, a list of `RecognizerResult` detections, and an operator config, then returns an `EngineResult` with the anonymized text and an audit trail. It knows nothing about how PII was detected.

## The Reverse-Loop Algorithm

Replacements are applied **right-to-left** (descending by `start` index). This ensures that replacing a span doesn't shift the indices of spans that come before it in the text.

```
Original:  "田中太郎の電話番号は090-1234-5678です"
                                          ← process this first
                  ← then this
```

## Operator Assignment

The YAML operator config maps entity types to operators:

```yaml
operators:
  PERSON:
    method: replace
    value: "<氏名>"
  PHONE_NUMBER:
    method: mask
    char: "*"
    from_end: 4
```

Each entity type gets exactly one operator. If an entity type is not in the config, the `keep` operator is used (text passes through unchanged).

## Changing Default Behavior

1. Copy `defaults/operators.yaml` to your own file.
2. Modify the operator assignments.
3. Pass it via CLI: `--rules my_operators.yaml`

Or programmatically:

```python
from besshouka.anonymizer.engine import anonymize

config = {"PERSON": {"method": "redact"}}
result = anonymize(text, recognizer_results, config)
```

## Available Operators

See [operators/README.md](operators/README.md) for the full list and how to write your own.
