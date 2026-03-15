import logging
from typing import Tuple

from doti18n.icumf import ICUMF, TextNode
from doti18n.icumf.nodes import FormatNode, MessageNode, TagNode

logger = logging.getLogger("doti18n.stub")


# ruff: noqa: C901
def generate_icumf_stub(name: str, string: str) -> Tuple[str, bool]:
    """
    Generate a stub signature for a formatted ICU message string.

    Treating ALL variables as named keyword-only arguments.
    """
    # doti18n require `other`, but we don't need it for stub
    icumf = ICUMF(strict=False, require_other=False)

    try:
        stack = icumf.get_ast(string)
    except Exception as e:
        logger.warning(f"Failed to parse ICU message. Message: {string} Error: {e}")
        return f"{name}: str = {repr(string)}", False

    if isinstance(stack, list) and len(stack) == 1 and isinstance(stack[0], TextNode):
        return f"{name}: str = {repr(string)}", False

    required_kwargs: dict[str, str] = {}
    while stack:
        node = stack.pop()

        if isinstance(node, (FormatNode, MessageNode)):
            if node.name not in required_kwargs:
                required_kwargs[node.name] = "Any"

            if isinstance(node, MessageNode):
                if node.type in ("plural", "selectordinal"):
                    required_kwargs[node.name] = "int"
                elif node.type == "select":
                    required_kwargs[node.name] = "Union[str, Any]"

                for child_nodes in node.options.values():
                    stack.extend(child_nodes)
        elif isinstance(node, TagNode):
            if node.name == "link":
                required_kwargs["link"] = "str"
            stack.extend(node.children)

    if not required_kwargs:
        return f"{name}: str = {repr(string)}", False

    parts = ["self", "*"]
    sorted_kwargs = sorted(list(required_kwargs.keys()))
    sorted_kwargs.append("formatter")

    for k in sorted_kwargs:
        arg_type = required_kwargs[k]
        if k == "count":
            arg_type = "int"
        if k == "formatter":
            arg_type = "BaseFormatter"
        parts.append(f"{k}: {arg_type}")

    sig_str = ", ".join(parts)
    message_docs = f'"""{repr(string)[1:-1]}"""\n'
    return f"def {name}({sig_str}) -> str:\n        {message_docs}\n        ...", True
