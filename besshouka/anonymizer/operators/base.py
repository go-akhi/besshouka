"""Abstract base class for all anonymization operators."""

from abc import ABC, abstractmethod


class BaseOperator(ABC):
    """Base class that all operators must subclass.

    Subclasses must implement operate() which takes the original PII text
    and a params dict, and returns the transformed string.
    """

    @abstractmethod
    def operate(self, text: str, params: dict) -> str:
        """Transform the PII text according to the operator's logic.

        Args:
            text: The original PII snippet.
            params: Operator-specific configuration from the YAML rules.

        Returns:
            The transformed string.
        """
        ...
