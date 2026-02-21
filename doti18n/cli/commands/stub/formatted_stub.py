import re
from typing import Tuple, Set, Any

PLACEHOLDER_REGEX = re.compile(
    r"""
        # Escaped sequences: {{, }}, %%, $$
        (?P<py_escape>\{\{|}}) |
        (?P<c_escape>%%) |
        (?P<shell_escape>\$\$) |

        # Python-style placeholders: {key:fmt}, {0:fmt}, {:fmt}
        (?P<python>
            \{
            (?P<python_key>[a-zA-Z0-9_]*)
            (?P<python_format>:[^}]+)?
            }
        ) |

        # C-style placeholders: %(key)s, %1$s, %s
        (?P<c_style>
            %
            (?:
                \((?P<c_key>[a-zA-Z0-9_]+)\) |
                (?P<c_index>[1-9]\d*)\$
            )?
            (?P<c_format>[+\-\#0-9.]*[diouxXeEfFgGcrsa%])
        ) |

        # Shell-style placeholders: $key, ${key}, $0, ${1}
        (?P<shell>
            \$
            (?:
                \{(?P<shell_braced_key>[a-zA-Z0-9_]+)} |
                (?P<shell_simple_key>[a-zA-Z0-9_]+)
            )
        )
    """,
    re.VERBOSE,
)


# ruff: noqa C901
def generate_formatted_stub(name: str, string: str) -> Tuple[str, bool]:
    """Generate a stub signature for a formatted string entry."""
    required_kwargs: dict[str, str] = {}
    used_indices = set()
    seq_cursor = 0
    matches = PLACEHOLDER_REGEX.finditer(string)

    for match in matches:
        groups = match.groupdict()

        if groups["py_escape"] or groups["c_escape"] or groups["shell_escape"]:
            continue

        if groups["c_style"] and groups["c_format"] == "%":
            continue

        is_named = False
        key = None
        index = None
        is_sequential = False
        placeholder_type = "Any"

        if groups["python"]:
            raw_key = groups["python_key"]
            fmt = groups.get("python_format")
            if fmt:
                if any(c in fmt for c in "di"):
                    placeholder_type = "int"
                elif any(c in fmt for c in "eEfgG%"):
                    placeholder_type = "float"
                else:
                    placeholder_type = "str"

            if raw_key:
                if raw_key.isdigit():
                    index = int(raw_key)
                else:
                    key = raw_key
                    is_named = True
            else:
                is_sequential = True

        elif groups["c_style"]:
            c_key = groups["c_key"]
            c_index = groups["c_index"]
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
                key = c_key
                is_named = True
            else:
                is_sequential = True

        elif groups["shell"]:
            s_key = groups["shell_braced_key"] or groups["shell_simple_key"]
            if s_key:
                if s_key.isdigit():
                    index = int(s_key)
                else:
                    key = s_key
                    is_named = True

        if is_named and key is not None:
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
        return f"{name}: str = {repr(string)}", False

    sig_str = ", ".join(parts)
    return f"def {name}({sig_str}) -> str: ...", True
