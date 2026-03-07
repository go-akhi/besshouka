"""Hash operator \u2014 replaces PII with a salted SHA-256 hex digest."""

import hashlib

from besshouka.anonymizer.operators.base import BaseOperator


class HashOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        salt = params.get("salt", "")
        return hashlib.sha256(f"{salt}{text}".encode("utf-8")).hexdigest()
