"""Tests for the custom operator (dynamic function import)."""

import pytest

from besshouka.anonymizer.operators.custom import CustomOperator


class TestCustomOperator:

    def setup_method(self):
        self.operator = CustomOperator()

    def test_import_and_call_function(self):
        """Should dynamically import and call the specified function."""
        result = self.operator.operate(
            "田中太郎",
            {"function": "tests.conftest.sample_custom_function"},
        )
        assert result == "郎太中田"  # reversed

    def test_params_passed_through(self):
        """Extra YAML params (excluding method/function) should be passed to the function."""
        result = self.operator.operate(
            "田中太郎",
            {
                "function": "tests.conftest.sample_custom_function_with_params",
                "prefix": "[",
                "suffix": "]",
            },
        )
        assert result == "[田中太郎]"

    def test_missing_function_key_raises(self):
        """Should raise an error if 'function' key is not in params."""
        with pytest.raises((KeyError, ValueError)):
            self.operator.operate("田中太郎", {})

    def test_nonexistent_module_raises(self):
        """Should raise ImportError for a module that doesn't exist."""
        with pytest.raises((ImportError, ModuleNotFoundError)):
            self.operator.operate(
                "田中太郎",
                {"function": "nonexistent_module.nonexistent_func"},
            )

    def test_nonexistent_function_raises(self):
        """Should raise AttributeError for a function that doesn't exist in the module."""
        with pytest.raises(AttributeError):
            self.operator.operate(
                "田中太郎",
                {"function": "tests.conftest.nonexistent_function"},
            )

    def test_method_and_function_excluded_from_params(self):
        """The 'method' and 'function' keys should not be passed to the user function."""
        # sample_custom_function_with_params uses params dict —
        # if 'method' or 'function' leak in, the output would include them
        result = self.operator.operate(
            "test",
            {
                "method": "custom",
                "function": "tests.conftest.sample_custom_function_with_params",
                "prefix": ">>",
                "suffix": "<<",
            },
        )
        assert result == ">>test<<"
