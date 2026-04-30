from typing import Any, Iterable, Tuple

from doti18n.wrapped.string import PLACEHOLDER_REGEX

PLURAL_ORDER = ("zero", "one", "two", "few", "many", "other")

_INT_FMT_CHARS = frozenset("dfi")
_FLOAT_FMT_CHARS = frozenset("eEfgG%")


def _python_placeholder_type(fmt: str | None) -> str:
    if not fmt:
        return "Any"
    if _INT_FMT_CHARS.intersection(fmt):
        return "int"
    if _FLOAT_FMT_CHARS.intersection(fmt):
        return "float"
    return "str"


def _collect_placeholders(texts: Iterable[str], types: dict[str, str]) -> tuple[dict[str, str], dict[int, str]]:
    """Collect placeholder information from formatted strings."""
    required_kwargs: dict[str, str] = {}
    used_indices: dict[int, str] = {}

    for text in texts:
        seq_cursor = 0

        for match in PLACEHOLDER_REGEX.finditer(text):
            if match.group("py_escape") or not match.group("python"):
                continue

            raw_key = match.group("python_key")
            p_type = _python_placeholder_type(match.group("python_format"))

            if raw_key:
                root_key = raw_key.split(".")[0].split("[")[0]
                if root_key.isdigit():
                    index = int(root_key)
                    if used_indices.get(index, "Any") == "Any":
                        used_indices[index] = p_type
                else:
                    final_type = types.get(root_key, p_type)
                    if required_kwargs.get(root_key, "Any") == "Any":
                        required_kwargs[root_key] = final_type
            else:
                while seq_cursor in used_indices:
                    seq_cursor += 1
                used_indices[seq_cursor] = p_type
                seq_cursor += 1

    return required_kwargs, used_indices


def _build_signature(required_kwargs: dict[str, str], used_indices: dict[int, str], is_plural: bool = False) -> str:
    parts = ["self"]
    if is_plural:
        parts.append("_n: int")

    if used_indices:
        max_pos = max(used_indices)
        parts.extend(f"_{i}: {used_indices.get(i, 'Any')}" for i in range(max_pos + 1))
        parts.append("/")
    else:
        max_pos = -1

    if required_kwargs:
        if max_pos == -1:
            parts.append("*")
        parts.extend(f"{k}: {required_kwargs[k]}" for k in sorted(required_kwargs))

    return ", ".join(parts)


def _build_plural_doc_block(plural_items: dict[str, str]) -> str:
    if not plural_items:
        return ""
    lines = "\n".join(f"    {k}: {v!r}" for k, v in plural_items.items())
    return f'    """\n{lines}\n    """'


def generate_formatted_stub(name: str, string: str, types: dict[str, str]) -> Tuple[str, bool]:
    """Generate a stub signature for a formatted string entry."""
    required_kwargs, used_indices = _collect_placeholders([string], types)
    if not used_indices and not required_kwargs:
        if "{{" in string or "}}" in string:
            return f"def {name}(self) -> str: ...", True
        return f"{name}: str = {string!r}", False

    sig_str = _build_signature(required_kwargs, used_indices)
    message_docs = f'"""{repr(string)[1:-1]}"""'

    return f"def {name}({sig_str}) -> str:\n        {message_docs}\n        ...", True


def generate_plural_stub(key: str, value: Any, types: dict[str, str]) -> str:
    """Generate a stub signature for a pluralizable string entry."""
    if not isinstance(value, dict):
        return f"{key}: Any = {value!r}"

    plural_items = {k: v for k in PLURAL_ORDER if isinstance(v := value.get(k), str)}
    required_kwargs, used_indices = _collect_placeholders(plural_items.values(), types)
    for coll in ("_n", "n", "count"):
        required_kwargs.pop(coll, None)

    sig_str = _build_signature(required_kwargs, used_indices, is_plural=True)
    doc_block = _build_plural_doc_block(plural_items)

    if doc_block:
        return f"def {key}({sig_str}) -> str:\n{doc_block}\n    ...\n"

    return f"def {key}({sig_str}) -> str:\n    ...\n"
