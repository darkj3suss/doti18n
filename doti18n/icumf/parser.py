# Original code by SirStendec.
# Repository: https://github.com/SirStendec/pyicumessageformat
# MIT License
#
# Copyright (c) 2021 Mike deBeaubien <sir@stendec.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import List, Optional, Union, TypedDict
from .nodes import FormatNode, MessageNode, Node, TagNode, TextNode


# --- Constants --- #
CHAR_OPEN = "{"
CHAR_CLOSE = "}"
CHAR_TAG_OPEN = "<"
CHAR_TAG_CLOSE = "/"
CHAR_TAG_END = ">"
CHAR_SEP = ","
CHAR_HASH = "#"
CHAR_ESCAPE = "'"
OFFSET = "offset:"
VAR_CHARS = [CHAR_OPEN, CHAR_CLOSE]
TAG_CHARS = [CHAR_TAG_OPEN, CHAR_TAG_CLOSE, CHAR_TAG_END]
TAG_CLOSING = CHAR_TAG_CLOSE + CHAR_TAG_END
TAG_END = CHAR_TAG_OPEN + CHAR_TAG_CLOSE
CLOSE_TAG: dict = {}
SEP_OR_CLOSE = "{} or {}".format(CHAR_SEP, CHAR_CLOSE)
# --- Constants --- #


class ParserContext(TypedDict):
    msg: str
    len: int
    i: int
    depth: int


class ParserError(Exception):
    """Base class for parser errors."""

    pass


class UnexpectedCharError(ParserError):
    def __init__(self, char: str, index: int):
        super().__init__(f'Unexpected "{char}" at position {index}')


class ExpectedCharError(ParserError):
    def __init__(self, expected: str, found: str, index: int):
        super().__init__(f'Expected {expected} at position {index} but found "{found}"')


# ruff: noqa C901
class Parser:
    def __init__(
        self,
        subnumeric_types: Optional[List[str]] = None,
        submessage_types: Optional[List[str]] = None,
        depth_limit: int = 50,
        allow_tags: bool = True,
        strict_tags: bool = True,
        tag_prefix: Optional[str] = None,
        allow_format_spaces: bool = True,
        require_other: bool = True,
    ):
        """
        Initialize the parser with configuration options.

        :param subnumeric_types: List of formatters that are considered subnumeric.
        :param submessage_types: List of formatters that are considered submessage.
        :param depth_limit: Limit of recursion depth for nested messages.
        :param allow_tags: Parse HTML/XML-like tags if True.
        :param strict_tags: Analyze tag pairs strictly if True.
        :param tag_prefix: Prefix that tags must start with to be considered valid.
        :param allow_format_spaces: Allow spaces in format arguments.
        :param require_other: Always require `other` option in submessage types.
        """
        self.subnumeric_types = ["plural", "selectordinal"] if subnumeric_types is None else subnumeric_types
        self.submessage_types = ["plural", "selectordinal", "select"] if submessage_types is None else submessage_types
        self.depth_limit = depth_limit
        self.allow_tags = allow_tags
        self.strict_tags = strict_tags
        self.tag_prefix = tag_prefix
        self.allow_format_spaces = allow_format_spaces
        self.require_other = require_other

    def parse(self, message: str) -> List[Node]:
        """Parse the given ICUMF message string into an AST."""
        if not isinstance(message, str):
            raise TypeError("Input must be a string")

        context: ParserContext = {"msg": message, "len": len(message), "i": 0, "depth": 0}

        result = self._parse_block(context)
        if context["i"] < context["len"]:
            raise UnexpectedCharError(message[context["i"]], context["i"])

        return result

    def _parse_block(self, context: ParserContext, parent_node: Optional[Node] = None) -> List[Node]:
        nodes: List[Node] = []
        msg = context["msg"]
        length = context["len"]

        while context["i"] < length:
            char = msg[context["i"]]
            if char == CHAR_CLOSE:
                if parent_node is None:
                    raise UnexpectedCharError(char, context["i"])

                break

            if self.allow_tags and self._is_tag_closing(context):
                if isinstance(parent_node, TagNode):
                    break

            if char == CHAR_HASH:
                if isinstance(parent_node, MessageNode) and parent_node.type in self.subnumeric_types:
                    nodes.append(FormatNode(name=parent_node.name, type="count", is_hash=True))
                    context["i"] += 1
                    continue

            if char == CHAR_OPEN:
                nodes.append(self._parse_argument(context))
                continue

            if self.allow_tags and char == CHAR_TAG_OPEN and self._can_read_tag(context):
                tag_node = self._parse_tag(context)
                if tag_node:
                    nodes.append(tag_node)
                    continue

            text = self._parse_text(context, parent_node)
            if text:
                nodes.append(TextNode(value=text))

        return nodes

    def _parse_text(self, context: ParserContext, parent_node: Optional[Node]) -> str:
        msg = context["msg"]
        length = context["len"]
        text = ""

        is_subnumeric = False
        if isinstance(parent_node, MessageNode) and parent_node.type in self.subnumeric_types:
            is_subnumeric = True

        while context["i"] < length:
            char = msg[context["i"]]

            if char == CHAR_OPEN or char == CHAR_CLOSE:
                break

            if char == CHAR_HASH and is_subnumeric:
                break

            if self.allow_tags:
                if char == CHAR_TAG_OPEN and self._can_read_tag(context) or self._is_tag_closing(context):
                    break

            if char == CHAR_ESCAPE:
                if context["i"] + 1 < length:
                    next_char = msg[context["i"] + 1]
                    if next_char in [CHAR_ESCAPE, CHAR_OPEN, CHAR_CLOSE, CHAR_HASH] or (
                        self.allow_tags and next_char == CHAR_TAG_OPEN
                    ):
                        text += next_char
                        context["i"] += 2
                        continue

                text += char
                context["i"] += 1
            else:
                text += char
                context["i"] += 1

        return text

    def _parse_argument(self, context: ParserContext) -> Union[FormatNode, MessageNode]:
        msg = context["msg"]
        context["i"] += 1
        self._skip_space(context)
        name = self._parse_name(context)
        if not name:
            raise ExpectedCharError("argument name", msg[context["i"]], context["i"])

        self._skip_space(context)

        if context["i"] < context["len"] and msg[context["i"]] == CHAR_CLOSE:
            context["i"] += 1
            return FormatNode(name=name)

        if msg[context["i"]] != CHAR_SEP:
            raise ExpectedCharError(", or }", msg[context["i"]], context["i"])
        context["i"] += 1
        self._skip_space(context)

        arg_type = self._parse_name(context)
        if not arg_type:
            raise ExpectedCharError("argument type", msg[context["i"]], context["i"])

        self._skip_space(context)

        if context["i"] < context["len"] and msg[context["i"]] == CHAR_CLOSE:
            context["i"] += 1
            if arg_type in self.submessage_types:
                raise ParserError(f"Type '{arg_type}' requires options")
            return FormatNode(name=name, type=arg_type)

        if msg[context["i"]] != CHAR_SEP:
            raise ExpectedCharError(", or }", msg[context["i"]], context["i"])
        context["i"] += 1
        self._skip_space(context)

        if arg_type in self.submessage_types:
            return self._parse_complex_argument(context, name, arg_type)
        else:
            style = self._parse_style_text(context)
            if context["i"] < context["len"] and msg[context["i"]] == CHAR_CLOSE:
                context["i"] += 1
                return FormatNode(name=name, type=arg_type, style=style.strip())
            else:
                raise ExpectedCharError("}", msg[context["i"]], context["i"])

    def _parse_complex_argument(self, context: ParserContext, name: str, arg_type: str) -> MessageNode:
        node = MessageNode(name=name, type=arg_type)
        msg = context["msg"]

        if arg_type in self.subnumeric_types:
            saved_i = context["i"]
            if msg[context["i"] :].startswith(OFFSET):
                context["i"] += len(OFFSET)
                self._skip_space(context)
                num_start = context["i"]

                while context["i"] < context["len"] and msg[context["i"]].isdigit():
                    context["i"] += 1

                if context["i"] > num_start:
                    node.offset = int(msg[num_start : context["i"]])
                    self._skip_space(context)
                else:
                    context["i"] = saved_i

        if context["depth"] >= self.depth_limit:
            raise ParserError("Maximum recursion depth exceeded")

        context["depth"] += 1

        while context["i"] < context["len"]:
            self._skip_space(context)
            if msg[context["i"]] == CHAR_CLOSE:
                break

            selector = self._parse_name(context)
            if not selector and msg[context["i"]] == "=":
                selector = "="
                context["i"] += 1
                while context["i"] < context["len"] and msg[context["i"]].isdigit():
                    selector += msg[context["i"]]
                    context["i"] += 1

            if not selector:
                raise ExpectedCharError("selector", msg[context["i"]], context["i"])

            self._skip_space(context)

            if msg[context["i"]] != CHAR_OPEN:
                raise ExpectedCharError("{", msg[context["i"]], context["i"])

            context["i"] += 1
            children = self._parse_block(context, parent_node=node)
            node.options[selector] = children
            if context["i"] < context["len"] and msg[context["i"]] == CHAR_CLOSE:
                context["i"] += 1

        context["depth"] -= 1
        if context["i"] < context["len"] and msg[context["i"]] == CHAR_CLOSE:
            context["i"] += 1
        else:
            raise ExpectedCharError("}", "EOF", context["i"])

        if self.require_other:
            should_check = True
            req = self.require_other
            if isinstance(req, list):
                should_check = arg_type in req
            if should_check and "other" not in node.options:
                raise ParserError(f"Missing 'other' option in {arg_type}; context: {node.name}")

        return node

    def _parse_tag(self, context: ParserContext) -> TagNode:
        msg = context["msg"]
        context["i"] += 1
        tag_name = self._parse_name(context)
        if not tag_name:
            raise ExpectedCharError("tag name", msg[context["i"]], context["i"])

        if context["i"] < context["len"] and msg[context["i"]] == CHAR_TAG_END:
            context["i"] += 1
        else:
            raise ExpectedCharError(">", msg[context["i"]], context["i"])

        tag_node = TagNode(name=tag_name)
        tag_node.children = self._parse_block(context, parent_node=tag_node)
        if context["i"] + 1 < context["len"] and msg[context["i"] : context["i"] + 2] == TAG_END:
            context["i"] += 2
            close_name = self._parse_name(context)
            if close_name != tag_name:
                if self.strict_tags:
                    raise ParserError(f"Tag mismatch: expected </{tag_name}>, found </{close_name}>")

            if context["i"] < context["len"] and msg[context["i"]] == CHAR_TAG_END:
                context["i"] += 1
            else:
                raise ExpectedCharError(">", msg[context["i"]], context["i"])

        return tag_node

    @staticmethod
    def _parse_style_text(context: ParserContext) -> str:
        start = context["i"]
        depth = 0
        msg = context["msg"]

        while context["i"] < context["len"]:
            char = msg[context["i"]]
            if char == CHAR_OPEN:
                depth += 1
            elif char == CHAR_CLOSE:
                if depth == 0:
                    break
                depth -= 1
            context["i"] += 1

        result: str = msg[start : context["i"]]
        return result

    @staticmethod
    def _parse_name(context: ParserContext) -> str:
        msg = context["msg"]
        length = context["len"]
        name = ""

        while context["i"] < length:
            char = msg[context["i"]]
            is_valid = char.isalnum() or char == "_" or char == "-"
            if not is_valid and not char.isspace():
                break

            if char.isspace():
                break

            name += char
            context["i"] += 1

        return name

    @staticmethod
    def _skip_space(context: ParserContext):
        msg = context["msg"]
        while context["i"] < context["len"] and msg[context["i"]].isspace():
            context["i"] += 1

    def _can_read_tag(self, context):
        msg = context["msg"]
        length = context["len"]
        start_index = context["i"] + 1

        if start_index >= length:
            return False

        prefix = self.tag_prefix
        if prefix:
            end_index = start_index + len(prefix)
            if end_index > length:
                return False
            return msg[start_index:end_index] == prefix
        return msg[start_index].isalpha()

    @staticmethod
    def _is_tag_closing(context: ParserContext):
        msg = context["msg"]
        i = context["i"]
        return msg[i : i + len(TAG_END)] == TAG_END
