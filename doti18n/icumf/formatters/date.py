import logging
from typing import TYPE_CHECKING, Optional, Sequence
from datetime import datetime

from ..nodes import Node, FormatNode, TextNode
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class DateFormatter(BaseFormatter):
    """
    Formatter for date messages.
    Date messages allow for formatting dates based on a given key.
    Example: {date, date, short} or {date, date, long} or {date, date, %d.%m.%Y}.

    If style is not provided, it falls back to a default format.
    """

    name = "date"
    is_subnumeric = False
    is_submessage = False
    style = {
        "short": "%d.%m.%Y",
        "long": "%d.%m.%Y %H:%M:%S",
    }

    def __init__(self, strict: bool):
        """Initialize the date formatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format a date message."""
        if not isinstance(node, FormatNode):
            raise TypeError("DateFormatter can only process FormatNode instances.")

        value = kwargs.get(node.name)
        if value is None:
            return self._throw(
                f"No date value provided for '{node.name}'.",
                ValueError,
            )
        if isinstance(value, int):
            date = datetime.fromtimestamp(value)
        elif isinstance(value, float):
            date = datetime.fromtimestamp(int(value))
        elif isinstance(value, str):
            try:
                date = datetime.fromisoformat(value)
            except ValueError as e:
                return self._throw(
                    f"Invalid date string provided for '{node.name}': {e}",
                    ValueError,
                )
        elif isinstance(value, datetime):
            date = value
        else:
            return self._throw(
                f"Unsupported date value type for '{node.name}': {type(value)}",
                TypeError,
            )

        style = self.style.get(node.style, None) or node.style
        return [TextNode(date.strftime(style))]

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
