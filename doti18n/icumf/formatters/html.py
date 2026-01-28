import logging
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import Node, TagNode, TextNode
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class HTMLFormatter(BaseFormatter):
    """
    Formatter for HTML tags inside messages.

    This formatter handles the conversion of certain tags to their HTML equivalents.
    Example: <link> becomes <a href="..."></a>.

    If an unsupported tag is encountered, it raises an error or logs a warning based on the strict mode.
    """

    name = "html"

    def __init__(self, strict: bool):
        """Initialize the HTMLFormatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format tags inside messages."""
        if not isinstance(node, TagNode):
            raise TypeError("HTMLFormatter can only process TagNode instances.")

        if node.name == "link":
            if not (link := kwargs.get("link")):
                return self._throw(
                    "No 'link' value provided for 'link' tag.",
                    ValueError,
                )

            return [TextNode(f'<a href="{link}">'), *node.children, TextNode("</a>")]

        else:
            return [TextNode(f"<{node.name}>"), *node.children, TextNode(f"</{node.name}>")]

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
