import logging
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import MessageNode, Node
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class SelectordinalFormatter(BaseFormatter):
    """
    Formatter for selectordinal messages.

    Selectordinal messages allow for different message options based on a given key.
    Example: {day, selectordinal, one {1st} two {2nd} few {3rd} other {#th}} day of the month.

    If no matching option is found, it falls back to the 'other' option.
    """

    name = "selectordinal"
    is_subnumeric = True
    is_submessage = True

    def __init__(self, strict: bool):
        """Initialize the select formatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format a selectordinal message."""
        if not isinstance(node, MessageNode):
            raise TypeError("SelectordinalFormatter can only process MessageNode instances.")

        options = node.options
        count = kwargs.get(node.name)
        if count is None:
            return self._throw(
                f"No count value provided for '{node.name}'.",
                ValueError,
            )

        count = abs(int(count))
        guess_option = f"={count}"
        if guess_option in options:
            return options[guess_option]

        try:
            option = t._ordinal_func(count)
        except Exception as e:
            self._logger.warning(
                f"Error determining selectordinal form for count '{count}': {e}. Falling back to 'other' option."
            )
            option = "other"

        return options[option]

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
