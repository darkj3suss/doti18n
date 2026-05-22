import logging

from doti18n.icumf import ICUMF, TextNode
from doti18n.icumf.nodes import FormatNode, MessageNode

logger = logging.getLogger("doti18n.stub")
_ICUMF = ICUMF(strict=False, require_other=False)


def _extract_icu_kwargs(stack: list, types: dict) -> dict[str, str]:
    kwargs: dict[str, str] = {}

    while stack:
        node = stack.pop()

        if isinstance(node, (FormatNode, MessageNode)):
            arg_type = "Any"

            if isinstance(node, MessageNode):
                if node.name in types:
                    arg_type = types[node.name]
                elif node.type in ("plural", "selectordinal"):
                    arg_type = "int"

                for child_nodes in node.options.values():
                    stack.extend(child_nodes)

            if kwargs.get(node.name, "Any") == "Any":
                kwargs[node.name] = arg_type

    if "count" in kwargs:
        kwargs["count"] = "int"

    return kwargs


def generate_icumf_stub(name: str, string: str, types: dict) -> tuple[str, bool]:
    """
    Generate a stub signature for a formatted ICU message string.

    Treating ALL variables as named keyword-only arguments.
    """
    try:
        stack = _ICUMF.get_ast(string)
    except Exception as e:
        logger.warning("Failed to parse ICU message. Message: %r Error: %s", string, e)
        return f"{name}: str = {string!r}", False

    if isinstance(stack, list) and len(stack) == 1 and isinstance(stack[0], TextNode):
        return f"{name}: str = {string!r}", False

    if not stack:
        return f"{name}: str = {string!r}", False

    required_kwargs = _extract_icu_kwargs(stack, types)
    if not required_kwargs:
        return f"{name}: str = {string!r}", False

    parts = ["self", "*"]
    parts.extend(f"{k}: {required_kwargs[k]}" for k in sorted(required_kwargs))
    parts.append("formatter: BaseFormatter")
    sig_str = ", ".join(parts)
    message_docs = f'"""{repr(string)[1:-1]}"""'

    return f"def {name}({sig_str}) -> str:\n        {message_docs}\n        ...", True
