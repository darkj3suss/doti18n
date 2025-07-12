import logging


class NoneWrapper:
    _instances = {}

    def __new__(cls, locale_code: str, path: str):
        """
        Some advanced Singleton
        :param path: Path to the unresolved localization.
        :type path: str
        """
        if path not in cls._instances:
            cls._instances[path] = super().__new__(cls)
        return cls._instances[path]

    def __init__(self, locale_code: str, path: str):
        self._path = path
        self._locale_code = locale_code

    def __call__(self, *args, **kwargs):
        logger.warning(f"Localization for {self._path} is not found.")

    def __getattr__(self, name: str):
        full_key_path = '.'.join([self._path, name])
        logger.warning(
            f"Locale '{self._locale_code}': key/index path '{full_key_path}' not found. "
            "None will be returned."
        )
        return NoneWrapper(self._locale_code, f"{self._path}.{name}")

    def __bool__(self):
        return False

    def __eq__(self, other):
        return (
            getattr(other, "_path", None) == self._path and getattr(other, "_locale_code", None) == self._locale_code
            or other is None
        )

    def __iter__(self):
        return iter([])

    def __str__(self):
        return "None"

    def __repr__(self):
        return f"NoneWrapper('{self._locale_code}': {self._path})"


logger = logging.getLogger(NoneWrapper.__name__)
