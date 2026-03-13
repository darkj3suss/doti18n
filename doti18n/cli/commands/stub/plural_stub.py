from typing import Any

from doti18n.wrapped.string_wrapper import PLACEHOLDER_REGEX


# ruff: noqa C901
def generate_plural_stub(key: str, value: Any) -> str:
    """Generate a stub signature for a pluralizable string entry."""
    if not isinstance(value, dict):
        return f"{key}: Any = {repr(value)}"

    plural_order = ["zero", "one", "two", "few", "many", "other"]
    required_kwargs: dict[str, str] = {}
    used_indices = set()
    seq_cursor = 0
    plural_items = [(k, value[k]) for k in plural_order if k in value and isinstance(value[k], str)]
    for _name, s in plural_items:
        matches = PLACEHOLDER_REGEX.finditer(s)
        for match in matches:
            groups = match.groupdict()

            if groups.get("py_escape") or groups.get("c_escape") or groups.get("shell_escape"):
                continue

            if groups.get("c_style") and groups.get("c_format") == "%":
                continue

            is_named = False
            key_name = None
            index = None
            is_sequential = False
            placeholder_type = "Any"

            if groups.get("python"):
                raw_key = groups.get("python_key")
                fmt = groups.get("python_format")
                if fmt:
                    if any(c in fmt for c in "dfi"):
                        placeholder_type = "int"
                    elif any(c in fmt for c in "eEfgG%"):
                        placeholder_type = "float"
                    else:
                        placeholder_type = "str"

                if raw_key:
                    if raw_key.isdigit():
                        index = int(raw_key)
                    else:
                        key_name = raw_key
                        is_named = True
                else:
                    is_sequential = True

            elif groups.get("c_style"):
                c_key = groups.get("c_key")
                c_index = groups.get("c_index")
                c_format = groups.get("c_format")
                if c_format:
                    if any(c in c_format for c in "diouxX"):
                        placeholder_type = "int"
                    elif any(c in c_format for c in "eEfFgG"):
                        placeholder_type = "float"
                    elif any(c in c_format for c in "s"):
                        placeholder_type = "str"

                if c_index:
                    index = int(c_index)
                elif c_key:
                    key_name = c_key
                    is_named = True
                else:
                    is_sequential = True

            elif groups.get("shell"):
                s_key = groups.get("shell_braced_key") or groups.get("shell_simple_key")
                if s_key:
                    if s_key.isdigit():
                        index = int(s_key)
                    else:
                        key_name = s_key
                        is_named = True

            if is_named and key_name:
                if key_name not in required_kwargs or required_kwargs[key_name] == "Any":
                    required_kwargs[key_name] = placeholder_type
            elif index is not None:
                used_indices.add((index, placeholder_type))
            elif is_sequential:
                while any(i == seq_cursor for i, t in used_indices):
                    seq_cursor += 1
                used_indices.add((seq_cursor, placeholder_type))
                seq_cursor += 1

    # Use a safe internal name for the count parameter to avoid collision with placeholders
    count_param_name = "_n"
    # remove possible collisions
    for coll in (count_param_name, "n", "count"):
        if coll in required_kwargs:
            del required_kwargs[coll]

    parts = ["self", f"{count_param_name}: int"]
    max_pos_index = max(i for i, t in used_indices) if used_indices else -1
    if max_pos_index >= 0:
        pos_types = {i: t for i, t in used_indices}
        pos_args = [f"_{i}: {pos_types.get(i, 'Any')}" for i in range(max_pos_index + 1)]
        parts.extend(pos_args)
        parts.append("/")

    if required_kwargs:
        if max_pos_index == -1:
            parts.append("*")
        sorted_kwargs = sorted(list(required_kwargs.keys()))
        kw_args = [f"{k}: {required_kwargs[k]}" for k in sorted_kwargs]
        parts.extend(kw_args)

    sig_str = ", ".join(parts)
    doc_lines = []
    for name, text in plural_items:
        doc_lines.append(f"{name}: {repr(text)}")

    # indent doc lines so after the entire function is indented into the class,
    # all docstring lines will align equally under the method body
    indented_doc_lines = ["    " + line for line in doc_lines]
    if indented_doc_lines:
        doc_block = '    """\n' + "\n".join(indented_doc_lines) + '\n    """'
    else:
        doc_block = ""

    func_lines = []
    func_lines.append(f"def {key}({sig_str}) -> str:")
    if doc_block:
        func_lines.append(doc_block)

    func_lines.append("    ...\n")
    return "\n".join(func_lines)
