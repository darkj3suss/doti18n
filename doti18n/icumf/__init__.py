import logging
import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from .formatters import *
from .nodes import FormatNode, MessageNode, Node, TagNode, TextNode
from .parser import Parser

if TYPE_CHECKING:
    from doti18n import LocaleTranslator


class CompiledMessage:
    """Wrapper for compiled ICUMF expressions."""

    def __init__(
        self,
        engine: "ICUMF",
        nodes: List[Node],
        raw: str = "",
        formatter: Optional[Callable] = None,
    ):
        """Initialize the CompiledMessage with the ICUMF engine, parsed nodes, raw string, and optional formatter."""
        self.engine = engine
        self.raw = raw
        self.formatter = formatter
        self.is_cached = engine.cache_size > 0
        self.nodes: Tuple[Node, ...] | List[Node] = tuple(nodes) if self.is_cached else nodes
        self.t: Optional["LocaleTranslator"] = None

    def __call__(self, **kwargs) -> str:
        """Render the compiled message with the provided keyword arguments."""
        if not self.t:
            raise RuntimeError("CompiledMessage is not bound to a LocaleTranslator.")
        try:
            if self.is_cached:
                frozen_kwargs = tuple(sorted(kwargs.items())) if kwargs else tuple()
                if not isinstance(self.nodes, tuple):
                    self.nodes = tuple(self.nodes)
                return self.engine._cached_render(self.t, self.nodes, frozen_kwargs, self.formatter)
            else:
                if not isinstance(self.nodes, list):
                    self.nodes = list(self.nodes)
                return self.engine._render_nodes(self.t, self.nodes, self.formatter, **kwargs)

        except Exception as e:
            msg = f"Failed to render ICUMF message: {self.raw!r} with args {kwargs} | Error: {e}"

            if self.engine._strict:
                raise RuntimeError(msg) from None
            else:
                self.engine._logger.error(msg)
                return ""

    def bind(self, t: "LocaleTranslator"):
        """Bind LocaleTranslator to the object."""
        self.t = t

    def __repr__(self) -> str:
        """Return a debug representation of the CompiledMessage."""
        return f"<{self.__class__.__name__} raw={self.raw!r}>"

    def __str__(self) -> str:
        """Return the raw ICUMF string representation."""
        return self.raw


icumf_pattern = re.compile(r"\{\s*\w+\s*,\}")
html_pattern = re.compile(r"<\s*\w+.*?>")


class ICUMF:
    """Main class for ICUMF formatting."""

    def __init__(
        self, strict: bool = True, tag_formatter: Optional[BaseFormatter] = None, cache_size: int = 1024, **kwargs
    ):
        """
        Initialize the ICUMF formatter with available formatters.

        :param strict: Whether to enforce strict formatting rules.
        :param tag_formatter: The formatter class to use for tags.
        :param cache_size: The size of the cache for rendered entries.
        :param kwargs: Additional keyword arguments for ICUMF parser configuration.
        """
        self.cache_size = cache_size
        self.formatters = {}
        for formatter_name, formatter_cls in BaseFormatter._FORMATTERS.items():
            self.formatters[formatter_name] = formatter_cls(strict=strict)

        subnumeric_formatters = [name for name, fmt in self.formatters.items() if fmt.is_subnumeric]
        submussage_formatters = [name for name, fmt in self.formatters.items() if fmt.is_submessage]
        self.parser = Parser(subnumeric_formatters, submussage_formatters, **kwargs)
        if tag_formatter:
            if not isinstance(tag_formatter, BaseFormatter):
                raise TypeError(
                    f"tag_formatter must be an instance of BaseFormatter, got {type(tag_formatter).__name__}"
                )
            self.tag_formatter = tag_formatter
        else:
            self.tag_formatter = HTMLFormatter(strict=strict)

        self._strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)
        if cache_size is not None and cache_size > 0:
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
            raw_string = string[4:]
            return self.compile(self.parser.parse(raw_string), raw=raw_string)

        if not (icumf_pattern.search(string) or html_pattern.search(string)):
            return string

        try:
            ast = self.parser.parse(string)
        except Exception as e:
            self._throw(f"Error parsing ICUMF string: {e}", ValueError, logging.WARNING)
            return string
        else:
            return self.compile(ast, raw=string)

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

    def compile(self, nodes: List[Node], formatter: Optional[BaseFormatter] = None, raw: str = "") -> CompiledMessage:
        """Compile the parsed nodes into a callable CompiledMessage instance."""
        return CompiledMessage(self, nodes, raw=raw, formatter=formatter)

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
        nodes: List[Node] | Tuple[Node],
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
