"""Mask operator \u2014 replaces characters with a masking symbol."""

from besshouka.anonymizer.operators.base import BaseOperator


class MaskOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        char = params.get("char", "*")
        from_end = min(params.get("from_end", 0), len(text))
        if from_end == 0:
            return text
        return text[:-from_end] + char * from_end
