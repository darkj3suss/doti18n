from typing import Any
from .formatted_string_stub import PLACEHOLDER_REGEX


def generate_plural_stub(key: str, value: Any) -> str:
    if not isinstance(value, dict):
        return f"{key}: Any = {repr(value)}"

    plural_order = ["zero", "one", "two", "few", "many", "other"]
    required_kwargs = set()
    used_indices = set()
    seq_cursor = 0
    plural_items = [(k, value[k]) for k in plural_order if k in value and isinstance(value[k], str)]
    for _name, s in plural_items:
        matches = PLACEHOLDER_REGEX.finditer(s)
        for match in matches:
            groups = match.groupdict()

            if groups.get('py_escape') or groups.get('c_escape') or groups.get('shell_escape'):
                continue

            if groups.get('c_style') and groups.get('c_format') == '%':
                continue

            is_named = False
            key_name = None
            index = None
            is_sequential = False

            if groups.get('python'):
                raw_key = groups.get('python_key')
                if raw_key:
                    if raw_key.isdigit():
                        index = int(raw_key)
                    else:
                        key_name = raw_key
                        is_named = True
                else:
                    is_sequential = True

            elif groups.get('c_style'):
                c_key = groups.get('c_key')
                c_index = groups.get('c_index')
                if c_index:
                    index = int(c_index)
                elif c_key:
                    key_name = c_key
                    is_named = True
                else:
                    is_sequential = True

            elif groups.get('shell'):
                s_key = groups.get('shell_braced_key') or groups.get('shell_simple_key')
                if s_key:
                    if s_key.isdigit():
                        index = int(s_key)
                    else:
                        key_name = s_key
                        is_named = True

            if is_named and key_name:
                required_kwargs.add(key_name)
            elif index is not None:
                used_indices.add(index)
            elif is_sequential:
                while seq_cursor in used_indices:
                    seq_cursor += 1
                used_indices.add(seq_cursor)
                seq_cursor += 1

    # Use a safe internal name for the count parameter to avoid collision with placeholders
    count_param_name = "_n"
    # remove possible collisions
    for coll in (count_param_name, "n", "count"):
        if coll in required_kwargs:
            required_kwargs.discard(coll)

    parts = ["self", f"{count_param_name}: int"]
    max_pos_index = max(used_indices) if used_indices else -1
    if max_pos_index >= 0:
        pos_args = [f"_{i}: Any" for i in range(max_pos_index + 1)]
        parts.extend(pos_args)
        parts.append("/")

    if required_kwargs:
        if max_pos_index == -1:
            parts.append("*")
        sorted_kwargs = sorted(list(required_kwargs))
        kw_args = [f"{k}: Any" for k in sorted_kwargs]
        parts.extend(kw_args)

    sig_str = ", ".join(parts)
    doc_lines = []
    for name, text in plural_items:
        doc_lines.append(f"{name}: {repr(text)}")

    # indent doc lines so after the entire function is indented into the class,
    # all docstring lines will align equally under the method body
    indented_doc_lines = ["    " + line for line in doc_lines]
    if indented_doc_lines:
        doc_block = "    \"\"\"\n" + "\n".join(indented_doc_lines) + "\n    \"\"\""
    else:
        doc_block = ""

    func_lines = []
    func_lines.append(f"def {key}({sig_str}) -> str:")
    if doc_block:
        func_lines.append(doc_block)

    func_lines.append("    ...\n")
    return "\n".join(func_lines)
