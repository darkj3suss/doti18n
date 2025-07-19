import logging


class NoneWrapper:
    """
    A wrapper class to handle missing locale or path gracefully.

    This class is designed to provide a fallback mechanism when a specific locale or
    path is not found during runtime. It primarily serves as a way to log warnings and
    return default values, such as `None`, for missing keys or attributes. This can be
    useful in localized applications or scenarios where attribute lookups might fail.
    """

    def __init__(self, locale_code: str, path: str):
        """
        Initialize an instance of the class with a given locale code and path.

        :param locale_code: The locale code representing the language or region.
        :type locale_code: str
        :param path: The file path or directory associated with the instance.
        :type path: str
        """
        self._path = path
        self._locale_code = locale_code

    def __call__(self, *args, **kwargs):
        """Log a warning and return None."""
        logger.warning(f"Locale '{self._locale_code}': key/index path '{self._path}' not found. None will be returned.")

    def __getattr__(self, name: str):
        """Log a warning and return None."""
        full_key_path = ".".join([self._path, name])
        logger.warning(
            f"Locale '{self._locale_code}': key/index path '{full_key_path}' not found. " "None will be returned."
        )
        return NoneWrapper(self._locale_code, f"{self._path}.{name}")

    def __bool__(self):
        """Return False."""
        return False

    def __eq__(self, other):
        """Return True if another object is None or NoneWrapper."""
        return type(other) is NoneWrapper or other is None

    def __iter__(self):
        """Log a warning and return an empty iterator."""
        logger.warning(f"Locale '{self._locale_code}': key/index path '{self._path}' not found. None will be returned.")
        return iter([])

    def __str__(self):
        """Log a warning and return None."""
        logger.warning(f"Locale '{self._locale_code}': key/index path '{self._path}' not found. None will be returned.")
        return "None"

    def __repr__(self):
        """Return a string representation of the object."""
        return f"NoneWrapper('{self._locale_code}': {self._path})"


logger = logging.getLogger(__name__)
