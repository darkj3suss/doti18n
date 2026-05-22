import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..nodes import FormatNode, Node, TextNode
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class CountFormatter(BaseFormatter):
    """
    Formatter for `count` inside messages.

    This formatter handles the insertion of counts into messages.
    Example: You have # new messages.

    If no count is provided, it raises an error or logs a warning based on the strict mode.
    """

    name = "count"
    is_subnumeric = True
    is_submessage = False

    def __init__(self, strict: bool):
        """Initialize the count formatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Node | None]:
        """Format a hash (#) inside messages."""
        if not isinstance(node, FormatNode):
            raise TypeError("CountFormatter can only process FormatNode instances.")

        count = kwargs.get(node.name, "")
        if not count and self._strict:
            raise ValueError(f"No value provided for '{node.name}'.")

        if not isinstance(count, str):
            count = str(count)

        return [TextNode(count)]
