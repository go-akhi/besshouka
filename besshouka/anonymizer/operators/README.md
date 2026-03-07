# Operators — Transformation Plugins

Each operator takes a PII text snippet and a params dict, and returns the transformed string. All operators subclass `BaseOperator`.

## The BaseOperator Contract

```python
class BaseOperator(ABC):
    def operate(self, text: str, params: dict) -> str: ...
```

- `text` — the original PII snippet (e.g. `"田中太郎"`).
- `params` — operator-specific configuration from the YAML rules (everything under that entity type's config).
- Returns the transformed string.

## Built-in Operators

| Operator   | Method     | Example Params                     | Input         | Output          |
|------------|------------|------------------------------------|---------------|-----------------|
| Replace    | `replace`  | `{"value": "<氏名>"}`             | `田中太郎`    | `<氏名>`        |
| Mask       | `mask`     | `{"char": "*", "from_end": 2}`    | `田中太郎`    | `田中**`        |
| Redact     | `redact`   | `{}`                               | `田中太郎`    | *(empty)*       |
| Hash       | `hash`     | `{"salt": "secret"}`              | `田中太郎`    | `a3f2...` (hex) |
| Encrypt    | `encrypt`  | `{"key": "<fernet-key>"}`         | `田中太郎`    | `gAAA...` (b64) |
| Keep       | `keep`     | `{}`                               | `田中太郎`    | `田中太郎`      |
| Custom     | `custom`   | `{"function": "mod.func", ...}`   | `田中太郎`    | *(user-defined)*|

### Mask semantics

`from_end` specifies how many characters to mask counting from the end of the string:

- `from_end: 4` on `090-1234-5678` → `090-1234-****`
- `from_end: 2` on `田中太郎` → `田中**`

### Custom operator

The `custom` operator dynamically imports and calls any Python function. The function must be importable from the Python path.

YAML config:

```yaml
EMPLOYEE_ID:
  method: custom
  function: "my_company.transforms.redact_employee_id"
  preserve_prefix: true
```

The function must follow this contract:

```python
def redact_employee_id(text: str, params: dict) -> str:
    # params contains everything except 'method' and 'function'
    # In this case: {"preserve_prefix": True}
    ...
```

## How to Write Your Own Operator

### Without touching Besshouka code

Use the `custom` operator — point `function` to any importable Python function that takes `(text: str, params: dict) -> str`. No subclassing needed.

### As a built-in operator (for contributors)

1. Create a new `.py` file in this directory.
2. Subclass `BaseOperator`:

```python
from besshouka.anonymizer.operators.base import BaseOperator


class MyOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        # Your transformation logic here
        return transformed_text
```

3. Register it in `engine.py` by adding it to the `_OPERATORS` dict:

```python
from besshouka.anonymizer.operators.my_operator import MyOperator

_OPERATORS["my_method"] = MyOperator()
```

4. Use it in the YAML config:

```yaml
ENTITY_TYPE:
  method: my_method
  my_param: value
```
