class Doti18nError(Exception):
    """
    Base class for doti18n exceptions.

    You can catch all doti18n errors using this class.
    """


class ParseError(Doti18nError):
    """Exception raised when a locale file contains invalid data."""


class UnsupportedFileExtensionError(Doti18nError):
    """Exception raised when trying to load a file with an unsupported extension."""


class MissingFileExtensionError(Doti18nError):
    """Exception raised when trying to load a file without an extension."""


class InvalidLocaleDataError(Doti18nError):
    """Base class for exceptions related to invalid locale data."""


class InvalidLocaleDocumentError(InvalidLocaleDataError):
    """Exception raised when a locale file contains invalid data."""


class EmptyFileError(Doti18nError):
    """Exception raised when a locale file is empty."""


class LocaleNotLoadedError(Doti18nError):
    """Exception raised when any locale is not loaded or empty."""


class MultipleLocaleError(Doti18nError):
    """Base class for exceptions related to multiple locales in a file."""


class DefaultLocaleNotLoadedError(Doti18nError):
    """
    Exception raised when the default locale is not loaded.

    If you have only one locale, you can set it as the default locale.
    """
