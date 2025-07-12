import logging
from typing import Callable


class PluralWrapper:
    """
    Just wraps a plural handler function to make it callable.
    And add more convenience methods.
    """
    def __init__(self, func: Callable, path: str, strict: bool = False):
        self.func = func
        self.path = path
        self.strict = strict
        self.logger = logging.getLogger(__name__)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f"PluralHandlerWrapper(key='{self.path}')"

    def __str__(self):
        msg = f"PluralHandlerWrapper is not a string. Call it as a function, not as a string."
        if self.strict:
            raise TypeError(msg)

        self.logger.warning(msg)
