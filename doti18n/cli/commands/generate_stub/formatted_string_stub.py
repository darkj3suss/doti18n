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
def generate_stub_signature(name: str, string: str) -> Tuple[str, bool]:
    """Generate a stub signature for a formatted string entry."""
    required_kwargs: Set[Any] = set()
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

        if groups["python"]:
            raw_key = groups["python_key"]
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

        if is_named:
            required_kwargs.add(key)
        elif index is not None:
            used_indices.add(index)
        elif is_sequential:
            while seq_cursor in used_indices:
                seq_cursor += 1
            used_indices.add(seq_cursor)
            seq_cursor += 1

    parts = ["self"]
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

    if max_pos_index == -1 and not required_kwargs:
        return f"{name}: str = {repr(string)}", False

    sig_str = ", ".join(parts)
    return f"def {name}({sig_str}) -> str: ...", True
