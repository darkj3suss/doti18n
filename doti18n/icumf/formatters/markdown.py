import logging
from typing import TYPE_CHECKING, Optional, Sequence

from ..nodes import Node, TagNode, TextNode
from . import BaseFormatter

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class MarkdownFormatter(BaseFormatter):
    """
    Formatter for Markdown tags inside messages.

    This formatter handles the conversion of certain tags to their Markdown equivalents.
    Example: <bold>bold text</bold> becomes **bold text**.

    If an unsupported tag is encountered, it raises an error or logs a warning based on the strict mode.
    """

    name = "markdown"

    def __init__(self, strict: bool):
        """Initialize the MarkdownFormatter."""
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        """Format tags inside messages."""
        if not isinstance(node, TagNode):
            raise TypeError("MarkdownFormatter can only process TagNode instances.")

        if node.name == "link":
            if not (link := kwargs.get("link")):
                return self._throw(
                    "No 'link' value provided for 'link' tag.",
                    ValueError,
                )

            return [TextNode("["), *node.children, TextNode("]"), TextNode(f"({link})")]

        elif node.name in ["bold", "b", "strong"]:
            return [TextNode("**"), *node.children, TextNode("**")]

        elif node.name in ["italic", "i", "em"]:
            return [TextNode("__"), *node.children, TextNode("__")]

        elif node.name == "code":
            return [TextNode("`"), *node.children, TextNode("`")]

        else:
            return self._throw(f"Unsupported tag '{node.name}'.", ValueError)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> list:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return []
