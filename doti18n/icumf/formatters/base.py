from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import Node

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class BaseFormatter(ABC):
    """Base class for formatters."""

    _FORMATTERS: dict = {}
    name: str = "base"
    is_subnumeric = False
    is_submessage = False

    @abstractmethod
    def __init__(self, strict: bool):
        """
        Initialize the formatter.

        :param strict: Whether to enforce strict formatting rules.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """
        Format a message with the given variables.

        :param t: The `LocaleTranslator` instance that handles the formatting.
        :param node: The node to format.
        :param kwargs: Additional keyword arguments for formatting.
        :return: A list of nodes after formatting.
        """
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """Register subclasses based on their formatter names."""
        super().__init_subclass__()

        if hasattr(cls, "name"):
            BaseFormatter._FORMATTERS[cls.name] = cls
