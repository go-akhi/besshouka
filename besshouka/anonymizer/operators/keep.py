"""Keep operator \u2014 passes through the original text unchanged."""

from besshouka.anonymizer.operators.base import BaseOperator


class KeepOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        return text
