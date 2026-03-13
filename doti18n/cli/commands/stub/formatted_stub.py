import re
from typing import Tuple
from doti18n.wrapped.string_wrapper import PLACEHOLDER_REGEX


# ruff: noqa C901
def generate_formatted_stub(name: str, string: str, types: dict[str, str]) -> Tuple[str, bool]:
    """Generate a stub signature for a formatted string entry."""
    required_kwargs: dict[str, str] = {}
    used_indices = set()
    seq_cursor = 0
    matches = PLACEHOLDER_REGEX.finditer(string)

    for match in matches:
        groups = match.groupdict()

        if groups.get("py_escape"):
            continue

        is_named = False
        key = None
        index = None
        is_sequential = False
        placeholder_type = "Any"

        if groups.get("python"):
            raw_key = groups["python_key"]
            fmt = groups.get("python_format")
            if fmt:
                if any(ch in fmt for ch in "di"):
                    placeholder_type = "int"
                elif any(ch in fmt for ch in "eEfgG%"):
                    placeholder_type = "float"
                else:
                    placeholder_type = "str"

            if raw_key:
                root_match = re.match(r"^([^.\[]+)", raw_key)
                root_key = root_match.group(1) if root_match else raw_key

                if root_key.isdigit():
                    index = int(root_key)
                else:
                    key = root_key
                    is_named = True
            else:
                is_sequential = True

        if is_named and key is not None:
            if key in types:
                placeholder_type = types[key]
            if key not in required_kwargs or required_kwargs[key] == "Any":
                required_kwargs[key] = placeholder_type
        elif index is not None:
            used_indices.add((index, placeholder_type))
        elif is_sequential:
            while any(i == seq_cursor for i, t in used_indices):
                seq_cursor += 1
            used_indices.add((seq_cursor, placeholder_type))
            seq_cursor += 1

    parts = ["self"]
    max_pos_index = max(i for i, t in used_indices) if used_indices else -1
    if max_pos_index >= 0:
        pos_types = {i: t for i, t in used_indices}
        pos_args = [f"_{i}: {pos_types.get(i, 'Any')}" for i in range(max_pos_index + 1)]
        parts.extend(pos_args)
        parts.append("/")

    if required_kwargs:
        if max_pos_index == -1:
            parts.append("*")

        sorted_keys = sorted(list(required_kwargs.keys()))
        kw_args = [f"{k}: {required_kwargs[k]}" for k in sorted_keys]
        parts.extend(kw_args)

    if max_pos_index == -1 and not required_kwargs:
        if "{{" in string or "}}" in string:
            return f"def {name}(self) -> str: ...", True
        else:
            return f"{name}: str = {repr(string)}", False

    sig_str = ", ".join(parts)
    return f"def {name}({sig_str}) -> str: ...", True
