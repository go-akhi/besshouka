"""Redact operator \u2014 completely removes the PII text."""

from besshouka.anonymizer.operators.base import BaseOperator


class RedactOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        return ""
