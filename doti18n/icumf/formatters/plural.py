import logging
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import MessageNode, Node
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class PluralFormatter(BaseFormatter):
    """
    Formatter for plural messages.

    This formatter selects the appropriate plural form based on a count value.
    Example: {count, plural, one {1 item} other {# items}}.

    If no count value is provided, it raises an error or logs a warning based on the strict mode.
    """

    name = "plural"
    is_subnumeric = True
    is_submessage = True

    def __init__(self, strict: bool):
        """Initialize the PluralFormatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format a plural message."""
        if not isinstance(node, MessageNode):
            raise TypeError("PluralFormatter can only process MessageNode instances.")
        options = node.options
        count = kwargs.get(node.name)
        if count is None:
            return self._throw(
                f"No count value provided for '{node.name}'.",
                ValueError,
            )

        guess_option = f"={count}"
        if guess_option in options:
            return options[guess_option]

        count = abs(int(count))
        try:
            option = t._main_plural_func(count)
        except Exception as e:
            self._logger.warning(
                f"Error determining plural form for count '{count}': {e}. " "Falling back to 'other' option."
            )
            option = "other"

        return options[option]

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
