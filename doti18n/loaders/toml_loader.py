import logging
import os
from pathlib import Path
from typing import Dict, List, NoReturn, Optional, Union

try:
    import tomllib
except ImportError:
    # tomllib is in stdlib since Python 3.11
    tomllib = None  # type: ignore

from ..errors import EmptyFileError, InvalidLocaleIdentifierError, ParseError, LocaleIdentifierMissingError, InvalidLocaleDocumentError
from ..utils import _get_locale_code
from .base_loader import BaseLoader


class TomlLoader(BaseLoader):
    """Loader for TOML files."""

    file_extension = ".toml"

    def __init__(self, strict: bool = False):
        """Initialize the TomlLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict

    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """
        Load and validate localization data from a TOML file.

        :param filepath: The full path to the TOML file to load.
        :return: A dictionary containing locale-specific data.
        :raises ImportError: If the tomllib package is not available.
        :raises FileNotFoundError: If the specified file does not exist.
        :raises ParseError: For issues in parsing the TOML file.
        :raises Exception: For any other unexpected exceptions during the load process.
        """
        if not tomllib:
            raise ImportError("tomllib is not available. TOML support requires Python 3.11+.")

        filename = os.path.basename(filepath)
        try:
            with open(filepath, "rb") as f:
                data = tomllib.load(f)
                if not data:
                    return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

                for root_key in ("locales", "translations"):
                    if not isinstance(data.get(root_key), list):
                        continue

                    documents = data[root_key]
                    if not documents:
                        return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

                    for locale in documents:
                        self._validate(filepath, locale)

                    return documents

                self._validate(filepath, data)
                locale_code = _get_locale_code(filename)
                self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
                return {locale_code: data}

        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except tomllib.TOMLDecodeError as e:
            self._throw(f"Error parsing TOML file '{filename}': {e}", ParseError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        return None

    def _validate(self, filepath: Union[str, Path], data: dict, path: Optional[List[str]] = None):
        path = path or []
        for key in data.keys():
            if not isinstance(key, str):
                self._throw(
                    f"TOML key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if not key.isidentifier():
                self._throw(
                    f"TOML key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if isinstance(data[key], dict):
                self._validate(filepath, data[key], path + [key])

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> Union[Dict, NoReturn]:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
