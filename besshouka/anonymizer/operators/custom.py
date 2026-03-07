"""Custom operator \u2014 dynamically imports and calls a user-provided Python function."""

import importlib

from besshouka.anonymizer.operators.base import BaseOperator


class CustomOperator(BaseOperator):

    def operate(self, text: str, params: dict) -> str:
        func_path = params["function"]
        module_path, func_name = func_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        # Pass all params except 'method' and 'function' to the user function
        user_params = {k: v for k, v in params.items() if k not in ("method", "function")}
        return func(text, user_params)
