# Defaults — Built-in Configuration Files

These YAML files ship with Besshouka and are used when no custom configuration is provided.

## recognizers.yaml — Built-in Patterns

Ships with regex patterns for Japanese PII:

| Name              | Entity Type       | What it matches                          |
|-------------------|-------------------|------------------------------------------|
| `mobile_phone`    | `PHONE_NUMBER`    | 090/080/070 mobile numbers               |
| `landline_phone`  | `PHONE_NUMBER`    | Landline numbers with area codes         |
| `tollfree_phone`  | `PHONE_NUMBER`    | 0120/0800 toll-free numbers              |
| `email`           | `EMAIL`           | Email addresses                          |
| `my_number`       | `MY_NUMBER`       | マイナンバー (12-digit, with/without spaces) |
| `postal_code`     | `POSTAL_CODE`     | 〒XXX-XXXX postal codes                  |
| `credit_card_visa_mc` | `CREDIT_CARD` | Visa/Mastercard numbers                  |
| `credit_card_amex`| `CREDIT_CARD`     | American Express numbers                 |
| `credit_card_jcb` | `CREDIT_CARD`     | JCB numbers                              |
| `bank_account`    | `BANK_ACCOUNT`    | 7-digit bank account numbers             |
| `drivers_license` | `DRIVERS_LICENSE` | 12-digit license numbers                 |
| `passport`        | `PASSPORT`        | 2 letters + 7 digits                     |

## operators.yaml — Default Operator Assignments

Maps each entity type to its default anonymization operator:

| Entity Type       | Operator  | Behaviour                                |
|-------------------|-----------|------------------------------------------|
| `PERSON`          | replace   | `<氏名>`                                |
| `LOCATION`        | replace   | `<住所>`                                |
| `ORGANIZATION`    | replace   | `<組織名>`                              |
| `PHONE_NUMBER`    | mask      | Last 4 characters masked with `*`        |
| `EMAIL`           | replace   | `<メール>`                              |
| `MY_NUMBER`       | redact    | Completely removed                       |
| `POSTAL_CODE`     | replace   | `<郵便番号>`                            |
| `CREDIT_CARD`     | mask      | Last 4 characters masked with `*`        |
| `BANK_ACCOUNT`    | mask      | Last 3 characters masked with `*`        |
| `DRIVERS_LICENSE`  | redact   | Completely removed                       |
| `PASSPORT`        | redact    | Completely removed                       |
| `DATE`            | replace   | `<日付>`                                |
| `TIME`            | replace   | `<時刻>`                                |
| `MONEY`           | replace   | `<金額>`                                |

## How to Override

Copy the default file, modify it, and pass it via CLI flags:

```bash
# Custom recognizer patterns
cp besshouka/defaults/recognizers.yaml my_recognizers.yaml
# Edit my_recognizers.yaml...
python -m besshouka.cli anonymize --recognizers my_recognizers.yaml "text"

# Custom operator rules
cp besshouka/defaults/operators.yaml my_operators.yaml
# Edit my_operators.yaml...
python -m besshouka.cli anonymize --rules my_operators.yaml "text"
```

## How to Extend

Add new entries to the YAML without removing built-in ones. For recognizers:

```yaml
recognizers:
  # Keep all existing entries, then add:
  - name: employee_id
    entity_type: EMPLOYEE_ID
    pattern: 'EMP-[A-Z]{2}\d{6}'
    score: 1.0
    source: custom
```

For operators:

```yaml
operators:
  # Keep all existing entries, then add:
  EMPLOYEE_ID:
    method: replace
    value: "<社員番号>"
```

## Schema Reference

### Recognizer entry

```yaml
- name: string          # Unique recognizer name
  entity_type: string   # Standardized entity type
  pattern: string       # Regex pattern
  score: float          # Confidence (0.0–1.0)
  source: string        # Optional, defaults to "regex_registry"
```

### Operator entry

```yaml
ENTITY_TYPE:
  method: string        # One of: replace, mask, redact, hash, encrypt, keep, custom
  # Additional params depend on the method:
  # replace: value (string)
  # mask: char (string), from_end (int)
  # hash: salt (string)
  # encrypt: key (string, Fernet key)
  # custom: function (string, dotted import path), plus any extra params
```
