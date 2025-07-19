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


class InvalidLocaleIdentifierError(Doti18nError):
    """
    Raised when a key in a locale file is not a valid Python identifier.

    Because doti18n allows accessing translations via dot notation (e.g., `t.messages.hello`),
    all keys must be valid Python variable names. They cannot contain hyphens,
    spaces, or start with a number.
    """


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


class UnexpectedMultiLocaleError(MultipleLocaleError):
    """
    Exception raised when a file contains multiple locales.

    It's not possible to use multiple locales for a single LocaleTranslator
    Instead of this, use preload=True in LocaleData, and use .get_translation() method.
    Or just use the scheme 'one locale = one file'
    """


class LocaleIdentifierMissingError(MultipleLocaleError):
    """
    Exception raised when a locale file does not contain a locale identifier.

    You can use multiple locales in one file, but you must specify a locale identifier
    for each locale. Basically this identifies "locale", but you can read more in detail
    in the documentation.
    """
