class StringWrapper(str):
    """A wrapper for a string value, which allows you to format strings by calling magic function `__call__`."""

    def __call__(self, *args, **kwargs):
        """Format the string using the given arguments and keyword arguments."""
        return self.format(*args, **kwargs)
