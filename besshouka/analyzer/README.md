# Analyzer — Detection Pipeline

The analyzer takes raw text and returns a list of `RecognizerResult` objects describing every PII span found. It knows nothing about what happens to those detections afterwards.

## Pipeline Order

```
Raw Text → normalize → recognizers → conflict resolution → list[RecognizerResult]
```

1. **Normalize** (`normalize.py`) — NFKC normalization (full-width → half-width) and Japanese dash standardization.
2. **Recognizers** (`recognizers/`) — Each recognizer scans the normalized text independently and returns its detections.
3. **Conflict Resolution** (`conflict_resolution.py`) — Overlapping detections from multiple recognizers are resolved into a non-overlapping set.

## Entity Type Taxonomy

All recognizers must use these standardized entity types:

| Entity Type      | Description                          |
|------------------|--------------------------------------|
| `PERSON`         | Personal names                       |
| `LOCATION`       | Addresses, place names               |
| `ORGANIZATION`   | Company/org names                    |
| `PHONE_NUMBER`   | Phone numbers (mobile, landline)     |
| `EMAIL`          | Email addresses                      |
| `MY_NUMBER`      | マイナンバー (12-digit individual number) |
| `POSTAL_CODE`    | Japanese postal codes (XXX-XXXX)     |
| `CREDIT_CARD`    | Credit card numbers                  |
| `BANK_ACCOUNT`   | Bank account numbers                 |
| `DRIVERS_LICENSE` | Driver's license numbers            |
| `PASSPORT`       | Passport numbers                     |
| `DATE`           | Dates                                |
| `TIME`           | Times                                |
| `MONEY`          | Monetary amounts                     |
| `QUANTITY`        | Numeric quantities                  |

## Adding a Custom Recognizer

### Without touching code — YAML registry

Add an entry to your recognizers YAML file:

```yaml
recognizers:
  - name: employee_id
    entity_type: EMPLOYEE_ID
    pattern: 'EMP-[A-Z]{2}\d{6}'
    score: 1.0
    source: custom
```

Pass it via CLI: `--recognizers my_recognizers.yaml`

### In code — subclass BaseRecognizer

See [recognizers/README.md](recognizers/README.md) for the step-by-step guide.
