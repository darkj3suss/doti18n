import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING

from ...utils import _NOT_FOUND
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

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Node | None]:
        """Format a select message."""
        if not isinstance(node, MessageNode):
            raise TypeError("SelectFormatter can only process MessageNode instances.")

        options = node.options
        option = kwargs.get(node.name, _NOT_FOUND)
        if option not in options:
            if "other" in options:
                if option is _NOT_FOUND:
                    self._logger.warning(f"No option provided for '{node.name}'. " f"Fallback to 'other'.")
                else:
                    self._logger.warning(
                        f"Option '{option}' is not valid option for '{node.name}'. " f"Fallback to 'other'."
                    )
                option = "other"
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
