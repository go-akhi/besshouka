# Orchestrator — Pipeline Coordination

The orchestrator is the only module that knows both the analyzer and anonymizer exist. It wires them together into a single `run()` function.

## Pipeline Execution Order

```python
ctx = run(text, recognizer_config, operator_config)
```

1. Create `ProcessingContext` with original text.
2. **Normalize** — NFKC normalization + Japanese dash cleanup.
3. **Recognize** — Run all recognizers (regex from YAML + GiNZA NER).
4. **Resolve conflicts** — Eliminate overlapping detections.
5. **Anonymize** — Apply operators per the operator config.
6. Return the completed `ProcessingContext`.

## ProcessingContext

The shared state object that travels through the pipeline:

| Field                | Type                     | Set by          |
|----------------------|--------------------------|-----------------|
| `original_text`      | `str`                    | Step 1 (init)   |
| `working_text`       | `str`                    | Step 2 (normalize) |
| `recognizer_results` | `list[RecognizerResult]` | Step 4 (resolve) |
| `engine_result`      | `EngineResult`           | Step 5 (anonymize) |
| `metadata`           | `dict`                   | Caller (optional) |

## Error Handling

- **GiNZA unavailable** — pipeline runs regex recognizers only, logs a warning. No crash.
- **Individual recognizer failure** — that recognizer is skipped, others still run. Logged as a warning.
- Entity types not in the operator config default to the `keep` operator (text passes through unchanged).

## Programmatic Usage

```python
from besshouka.config.loader import load_recognizer_config, load_operator_config
from besshouka.orchestrator.pipeline import run

rec_config = load_recognizer_config("recognizers.yaml")
op_config = load_operator_config("operators.yaml")

ctx = run("田中太郎の電話は090-1234-5678です", rec_config, op_config)

# Anonymized text
print(ctx.engine_result.text)

# Audit trail
for item in ctx.engine_result.items:
    print(f"{item.entity_type}: '{item.original_text}' → [{item.operator}]")

# Original text is always preserved
print(ctx.original_text)
```
