"""Replace operator \u2014 substitutes PII with a fixed value."""

from besshouka.anonymizer.operators.base import BaseOperator


class ReplaceOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        return params["value"]
