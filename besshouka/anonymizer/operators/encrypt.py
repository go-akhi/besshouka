"""Encrypt operator \u2014 encrypts PII with Fernet symmetric encryption."""

from cryptography.fernet import Fernet

from besshouka.anonymizer.operators.base import BaseOperator


class EncryptOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        f = Fernet(params["key"].encode())
        return f.encrypt(text.encode("utf-8")).decode("utf-8")
