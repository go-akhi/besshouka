# Besshouka

Besshouka is a local-first Japanese PII anonymization engine. It detects personally identifiable information (PII), payment card data (PCI), and protected health information (PHI) in Japanese text and transforms it according to user-configurable rules. The engine is stateless — it receives plain text, anonymizes it, and returns the result.

## Architecture

```
Text In → [Analyzer] → [Anonymizer] → Text Out
```

- **Analyzer** — detects PII using regex patterns and GiNZA NER. See [analyzer/README.md](analyzer/README.md).
- **Anonymizer** — transforms detected PII using pluggable operators. See [anonymizer/README.md](anonymizer/README.md).
- **Orchestrator** — wires the two together into a single pipeline. See [orchestrator/README.md](orchestrator/README.md).
- **Models** — shared data contracts used across modules. See [models/README.md](models/README.md).
- **Config** — YAML configuration loading and validation. See [config/README.md](config/README.md).
- **Defaults** — built-in recognizer patterns and operator rules. See [defaults/README.md](defaults/README.md).

## Installation

```bash
python -m venv env_besshouka
source env_besshouka/bin/activate
pip install -r requirements.txt
```

## CLI Usage

```bash
# Anonymize inline text
python -m besshouka.cli anonymize "田中太郎の電話番号は090-1234-5678です"

# Anonymize from file
python -m besshouka.cli anonymize --input document.txt --output anonymized.txt

# Anonymize with custom rules
python -m besshouka.cli anonymize --rules my_rules.yaml --recognizers my_patterns.yaml "text"

# Analyze only (show detections)
python -m besshouka.cli analyze "田中太郎の電話番号は090-1234-5678です"

# Analyze with score/source reasoning
python -m besshouka.cli analyze --explain "田中太郎の電話番号は090-1234-5678です"
```

## Programmatic Usage

```python
from besshouka.config.loader import load_recognizer_config, load_operator_config
from besshouka.orchestrator.pipeline import run

rec_config = load_recognizer_config("path/to/recognizers.yaml")
op_config = load_operator_config("path/to/operators.yaml")

ctx = run("田中太郎の電話番号は090-1234-5678です", rec_config, op_config)

print(ctx.engine_result.text)    # anonymized text
print(ctx.engine_result.items)   # audit trail
```

## Running Tests

```bash
# All tests (excluding slow GiNZA tests)
pytest tests/ -m "not slow"

# All tests including GiNZA
pytest tests/

# With coverage
pytest tests/ --cov=besshouka --cov-report=term-missing
```
