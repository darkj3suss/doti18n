import logging
from typing import Callable


class PluralWrapper:
    """
    Wrap a plural handler function to make it callable.

    And add more convenience methods.
    """

    __slots__ = ("func", "path", "strict", "logger")

    def __init__(self, func: Callable, path: str, strict: bool = False):
        """
        Initialize an instance with the provided function, path, and strictness flag.

        This constructor sets up the core attributes for an object, including the
        function to be used (`func`), the path associated with this instance (`path`),
        and whether the instance operates in strict mode (`strict`).

        :param func: The callable function associated with this instance.
        :param path: A string representing the path for this instance.
        :param strict: A boolean flag indicating if strict mode is enabled. Defaults to False.
        """
        self.func = func
        self.path = path
        self.strict = strict
        self.logger = logging.getLogger(__name__)

    def __call__(self, *args, **kwargs):
        """Call the wrapped plural handler function."""
        return self.func(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the object."""
        return f"PluralHandlerWrapper(key='{self.path}')"

    def __str__(self):
        """Raise an exception or log warning if called as a string."""
        msg = "PluralHandlerWrapper is not a string. Call it as a function, not as a string."
        if self.strict:
            raise TypeError(msg)

        self.logger.warning(msg)
