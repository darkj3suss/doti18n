import logging
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import MessageNode, Node
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class SelectFormatter(BaseFormatter):
    """
    Formatter for select messages.

    Select messages allow for different message options based on a given key.
    Example: {gender, select, male {He} female {She} other {They}} went to the store.

    If no matching option is found, it falls back to the 'other' option.
    """

    name = "select"
    is_subnumeric = False
    is_submessage = True

    def __init__(self, strict: bool):
        """Initialize the select formatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format a select message."""
        if not isinstance(node, MessageNode):
            raise TypeError("SelectFormatter can only process MessageNode instances.")

        options = node.options
        option = kwargs.get(node.name, None)
        if option not in options:
            if "other" in options:
                option = "other"
                self._logger.warning(f"No valid option provided for '{node.name}'. Fallback to 'other' option.")
            else:
                return self._throw(
                    f"No option provided for '{node.name}' " f"and 'other' option is missing.",
                    ValueError,
                )
        if not (result := options.get(option, None)):
            return self._throw(
                f"No message found for option '{option}' in '{node.name}'.",
                ValueError,
            )

        return result

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
