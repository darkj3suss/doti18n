import logging
from typing import Set, Tuple

from doti18n.icumf.nodes import FormatNode, MessageNode, TagNode
from doti18n.icumf.parser import Parser


def generate_icumf_stub(name: str, message: str) -> Tuple[str, bool]:
    """
    Generate a stub signature for a formatted ICU message string.

    Treating ALL variables as named keyword-only arguments.
    """
    # doti18n require `other`, but we don't need it for stub
    parser = Parser(require_other=False)

    try:
        stack = parser.parse(message)
    except Exception as e:
        logging.error(f"Failed to parse ICU message\nMessage: {message}\nError: {e}")
        return f"{name}: str = {repr(message)}", False

    required_kwargs: Set[str] = set()
    while stack:
        node = stack.pop()

        if isinstance(node, (FormatNode, MessageNode)):
            required_kwargs.add(node.name)

            if isinstance(node, MessageNode):
                for child_nodes in node.options.values():
                    stack.extend(child_nodes)
        elif isinstance(node, TagNode):
            if node.name == "link":
                required_kwargs.add("link")
            stack.extend(node.children)

    if not required_kwargs:
        return f"{name}: str = {repr(message)}", False

    parts = ["self", "*"]
    sorted_kwargs = sorted(list(required_kwargs))

    for k in sorted_kwargs:
        parts.append(f"{k}: Any")

    sig_str = ", ".join(parts)
    return f"def {name}({sig_str}) -> str: ...", True
