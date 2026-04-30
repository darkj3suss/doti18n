import logging
from typing import Callable


class PluralWrapper:
    """Wrap a plural handler function to make it callable."""

    __slots__ = ("func", "path", "strict", "_logger")

    def __init__(self, func: Callable, path: str, strict: bool = False):
        """Initialize an instance with the provided function, path, and strictness flag."""
        self.func = func
        self.path = path
        self.strict = strict
        self._logger = logging.getLogger(self.__class__.__name__)

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

        self._logger.warning(msg)
