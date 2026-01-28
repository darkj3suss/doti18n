from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class Node:
    """Base class for all node types in the message AST."""

    pass


@dataclass(slots=True)
class TextNode(Node):
    """Node for plain text segments in the message."""

    value: str

    def __repr__(self):
        """Return a string representation of the TextNode."""
        return f"Text('{self.value}')"


@dataclass(slots=True)
class FormatNode(Node):
    """Node for variable formatting. Also for hash(#) inside plural messages."""

    name: str
    type: Optional[str] = None  # 'date', 'number', 'time', etc.
    style: Optional[str] = None  # 'short', '::.00', 'percent', etc.
    is_hash: bool = False  # True, if this node represents a hash (#) in plural messages.

    def __repr__(self):
        """Return a string representation of the FormatNode."""
        parts = [self.name]
        if self.type:
            parts.append(self.type)
        if self.style:
            parts.append(self.style)
        return f"Format({', '.join(parts)})"


@dataclass
class MessageNode(Node):
    """Node for complex message structures like plural, selectordinal, select, etc."""

    name: str
    type: str  # 'plural', 'selectordinal', 'select'
    options: Dict[str, List[Node]] = field(default_factory=dict)
    offset: int = 0

    def __repr__(self):
        """Return a string representation of the MessageNode."""
        return f"Message({self.name}, {self.type}, options={list(self.options.keys())})"


@dataclass
class TagNode(Node):
    """Node for XML/HTML-like tags within the message."""

    name: str
    children: List[Node] = field(default_factory=list)

    def __repr__(self):
        """Return a string representation of the TagNode."""
        return f"Tag({self.name}, children={len(self.children)})"


__all__ = [
    "Node",
    "TextNode",
    "FormatNode",
    "MessageNode",
    "TagNode",
]
