import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..errors import (
    EmptyFileError,
    InvalidLocaleIdentifierError,
    ParseError,
)
from ..utils import _get_locale_code
from .base_loader import BaseLoader


class JsonLoader(BaseLoader):
    """Loader for JSON files."""
    file_extension = ".json"

    def __init__(self, strict: bool = False):
        """Initialize the JsonLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict

    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """
        Load and validate locale data from a JSON file.

        The method reads the contents of the file and validates them against the given structure.
        It returns the parsed data as a dictionary or a list of dictionaries, depending on the file content.

        :param filepath: The path to the JSON file to be loaded.
        :return: Parsed data from the JSON file. It could be a dictionary where the key
            is a locale code and the value is its corresponding data, or a list of
            dictionaries containing locale information.
        :raises EmptyFileError: Raised if the file exists but is empty.
        :raises ParseError: Raised if there is an issue with parsing the JSON in the file.
        :raises FileNotFoundError: Raised if the specified file does not exist.
        :raises Exception: Raised for any other unexpected errors during the file loading process.
        """
        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                if not data:
                    self._throw(f"Locale file '{filename}' is empty", EmptyFileError)
                    return {}

                if isinstance(data, list):
                    for locale in data:
                        self._validate(filepath, locale)

                    return data

                self._validate(filepath, data)
                locale_code = _get_locale_code(filename)
                self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
                return {locale_code: data}
        except json.decoder.JSONDecodeError as e:
            self._throw(f"Error parsing JSON file '{filename}': {e}", ParseError)
        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        return None

    def _validate(self, filepath: str, data: dict, path: Optional[List[str]] = None):
        path = path or []
        for key in data.keys():
            if not isinstance(key, str):
                self._throw(
                    f"JSON key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if not key.isidentifier():
                self._throw(
                    f"JSON key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if isinstance(data[key], dict):
                self._validate(filepath, data[key], path + [key])

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR):
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return None
