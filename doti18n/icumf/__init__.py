import logging
import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from .formatters import *
from .nodes import FormatNode, MessageNode, Node, TagNode, TextNode
from .parser import Parser

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


icumf_pattern = re.compile(r"\{\s*\w+\s*[,\}]")
html_pattern = re.compile(r"<\s*\w+.*?>")


class ICUMF:
    """Main class for ICUMF formatting."""

    def __init__(
        self, strict: bool = True, tag_formatter: type[BaseFormatter] = HTMLFormatter, cache_size: int = 1024, **kwargs
    ):
        """
        Initialize the ICUMF formatter with available formatters.

        :param strict: Whether to enforce strict formatting rules.
        :param tag_formatter: The formatter class to use for tags.
        :param cache_size: The size of the cache for rendered entries.
        :param kwargs: Additional keyword arguments for ICUMF parser configuration.
        """
        self.formatters = {}
        for formatter_name, formatter_cls in BaseFormatter._FORMATTERS.items():
            self.formatters[formatter_name] = formatter_cls(strict=strict)

        subnumeric_formatters = [name for name, fmt in self.formatters.items() if fmt.is_subnumeric]
        submussage_formatters = [name for name, fmt in self.formatters.items() if fmt.is_submessage]
        self.parser = Parser(subnumeric_formatters, submussage_formatters, **kwargs)
        self.tag_formatter = tag_formatter(strict)
        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)
        self._cached_render = lru_cache(maxsize=cache_size)(self._cached_render_)

    def parse(self, string: str) -> Any:
        """
        Parse the given string. If it's not in ICUMF format, return it as is.

        Forcing ICUMF parsing if the string starts with "icu:".

        :param string: The ICUMF formatted string to parse.
        :return: The parsed representation of the string (or the original string if not ICUMF).
        """
        if not isinstance(string, str):
            return string

        # explicit not ICUMF
        if string.startswith("!icu:"):
            return string

        # explicit ICUMF
        if string.startswith("icu:"):
            string = string[4:]
            return self.compile(self.parser.parse(string))

        if not (icumf_pattern.search(string) or html_pattern.search(string)):
            return string

        try:
            ast = self.parser.parse(string)
        except Exception as e:
            self._throw(f"Error parsing ICUMF string: {e}", ValueError, logging.WARNING)
            return string
        else:
            return self.compile(ast)

    def get_ast(self, string: str) -> Optional[List[Node]]:
        """
        Parse the input string and returns its corresponding Abstract Syntax Tree (AST).

        Fallback representation as a list of nodes.
        This method can handle ICU formatted strings, HTML-like strings, or plain text strings.

        :param string: The input string to be parsed.
        :type string: str
        :return: A list of nodes representing the Abstract Syntax Tree (AST) or a fallback
            representation as a single `TextNode` if parsing fails or is unnecessary.
        :rtype: Optional[List[Node]]
        """
        if not isinstance(string, str):
            return None

        if string.startswith("!icu:"):
            return [TextNode(string[5:])]

        if string.startswith("icu:"):
            return self.parser.parse(string[4:])

        if not (icumf_pattern.search(string) or html_pattern.search(string)):
            return [TextNode(string)]

        try:
            return self.parser.parse(string)
        except Exception:
            return [TextNode(string)]

    def compile(self, nodes: List[Node], formatter: Optional[BaseFormatter] = None) -> Callable:
        """
        Compile the parsed nodes into a callable formatter function.

        :param nodes: The list of parsed nodes.
        :param formatter: An optional formatter function to use for tags.
        :return: A callable function that formats strings based on the nodes.
        """
        tuple_nodes: Tuple = tuple(nodes)
        return lambda t, **kwargs: self._render_entry(t, tuple_nodes, **{"formatter": formatter, **kwargs})

    def _render_entry(self, t: "LocaleTranslator", nodes: Tuple[Node], **kwargs) -> str:
        formatter = kwargs.pop("formatter", None)
        frozen_kwargs = tuple(sorted(kwargs.items())) if kwargs else ()
        return self._cached_render(t, nodes, frozen_kwargs, formatter)

    def _cached_render_(
        self,
        t: "LocaleTranslator",
        nodes: Tuple[Node],
        frozen_kwargs: Tuple[Tuple[str, Any]],
        formatter: Optional[Callable] = None,
    ) -> str:
        kwargs = dict(frozen_kwargs)
        return self._render_nodes(t, list(nodes), formatter, **kwargs)

    def _render_nodes(
        self,
        t: "LocaleTranslator",
        nodes: List[Node],
        formatter: Optional[Callable] = None,
        **kwargs,
    ) -> str:
        text = []
        for node in nodes:
            if isinstance(node, TextNode):
                text.append(node.value)
                continue

            elif isinstance(node, (FormatNode, MessageNode)):
                if not (fmt := self.formatters.get(node.type)):
                    if isinstance(node, FormatNode) and not node.style:
                        # treat as simple variable replacement
                        value = kwargs.get(node.name, "")
                        text.append(str(value))
                        continue

                    self._throw(
                        f"Unknown formatter '{node.type}'.",
                        ValueError,
                    )
                    continue

                result = fmt(t, node, **kwargs)
                if isinstance(result, list):
                    text.append(self._render_nodes(t, result, formatter, **kwargs))
                else:
                    # just in case
                    text.append(str(result))

            elif isinstance(node, TagNode):
                tag_formatter = formatter or self.tag_formatter
                result = tag_formatter(t, node, **kwargs)
                if isinstance(result, list):
                    text.append(self._render_nodes(t, result, formatter, **kwargs))
                else:
                    # just in case
                    text.append(str(result))

        return "".join(text)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR):
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return ""
