import logging
import re

PLACEHOLDER_REGEX = re.compile(
    r"""
        (?P<py_escape>\{\{|}}) |
        (?P<python>
            \{
            (?P<python_key>[^{}:]*)
            (?P<python_format>:[^}]+)?
            }
        )
    """,
    re.VERBOSE,
)


class StringWrapper(str):
    """A wrapper for a string value, which allows you to format strings by calling magic function `__call__`."""

    def __call__(self, *args, **kwargs) -> str:
        """Format the string using the provided arguments and keyword arguments."""
        try:
            return self.format(*args, **kwargs)
        except Exception as e:
            logging.getLogger(self.__class__.__name__).warning(
                f"Failed to format string '{self}' with args {args} and kwargs {kwargs}. "
                f"Error: {e.__class__.__name__}: {e}"
            )
            temp = "".join(re.split(r"\{.*}", self))
            temp = temp.replace("{{", "{").replace("}}", "}")
            return temp
