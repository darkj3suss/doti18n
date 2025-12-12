import re
from typing import Any, Tuple

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
    re.VERBOSE
)


class StringWrapper(str):
    """A wrapper for a string value, which allows you to format strings by calling magic function `__call__`."""

    __slots__ = ("_formatter",)

    def __call__(self, *args, **kwargs) -> str:
        """
        Callable class method to format a string based on the presence of specific
        formatting placeholders. This method checks for particular placeholders such
        as '%' or '$' within the string and processes the string accordingly using
        the corresponding formatter method or the default format method.

        :param args: Positional arguments to be passed to the formatter or format methods.
        :param kwargs: Keyword arguments to be passed to the formatter or format methods.
        :return: A formatted string based on the specified placeholders and provided
                 arguments and keyword arguments.
        """
        if "%" in self or "$" in self:
            return self.formatter(*args, **kwargs)

        return self.format(*args, **kwargs)

    def formatter(self, *args, **kwargs) -> str:
        """
        Format a given string by replacing placeholders with corresponding values.

        This function supports various placeholder formats such as Python style,
        C-style, and shell-style placeholders. Each placeholder in the string is parsed
        and replaced with values provided in `args` or `kwargs`. If a placeholder refers
        to an argument index or key that is not provided, it is skipped.

        Examples of supported placeholders:
        - Python-style: {}, {0}, {name}, {value:.2f}
        - C-style: %s, %d, %(name)s, %1$d
        - Shell-style: $1, ${name}

        Escaped sequences:
        - `{{` and `}}` for Python style
        - `%%` for C style
        - `$$` for Shell style

        :param self: The input string that contains placeholders for formatting.
        :param args: Positional arguments used for replacing placeholders.
        :param kwargs: Keyword arguments used for replacing placeholders.
        :return: A formatted string with placeholders replaced by the provided values.
        """
        used_args = [False] * len(args)
        next_sequential_index = 0

        def get_next_seq_arg() -> Tuple[Any, bool]:
            """Find the next unused positional argument."""
            nonlocal next_sequential_index
            search_index = next_sequential_index
            while search_index < len(used_args):
                if not used_args[search_index]:
                    used_args[search_index] = True
                    next_sequential_index = search_index + 1
                    return args[search_index], True
                search_index += 1
            return None, False

        # noinspection PyStringFormat
        def replacer(match: re.Match) -> str:
            """Replace placeholders with their corresponding values."""
            groups = match.groupdict()

            if groups['py_escape']:
                return groups['py_escape'][0]
            if groups['c_escape']:
                return '%'
            if groups['shell_escape']:
                return '$'

            value: Any = None
            is_found = False
            if groups['python']:
                key = groups['python_key']
                if key.isdigit():
                    index = int(key)
                    if index < len(args):
                        value, is_found = args[index], True
                        used_args[index] = True
                elif key:
                    if key in kwargs:
                        value, is_found = kwargs[key], True
                else:
                    value, is_found = get_next_seq_arg()

            elif groups['c_style']:
                if groups['c_format'] == '%':
                    return '%'
                key, index_str = groups['c_key'], groups['c_index']
                if index_str:
                    index = int(index_str)
                    if 0 <= index < len(args):
                        value, is_found = args[index], True
                        used_args[index] = True
                elif key:
                    if key in kwargs:
                        value, is_found = kwargs[key], True
                else:
                    value, is_found = get_next_seq_arg()

            elif groups['shell']:
                key = groups['shell_braced_key'] or groups['shell_simple_key']
                if key:
                    if key.isdigit():
                        index = int(key)
                        if index < len(args):
                            value, is_found = args[index], True
                            used_args[index] = True
                    else:
                        if key in kwargs:
                            value, is_found = kwargs[key], True

            if not is_found:
                return ""

            try:
                if groups['python']:
                    format_spec = groups['python_format'] or ''
                    return f"{{value{format_spec}}}".format(value=value)
                if groups['c_style']:
                    return f"%{groups['c_format']}" % value
                if groups['shell']:
                    return str(value)

            except (ValueError, TypeError):
                return str(value)

            return match.group()

        # type: str
        return PLACEHOLDER_REGEX.sub(replacer, self)
