import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

from ..errors import (
    InvalidLocaleDocumentError,
    LocaleIdentifierMissingError,
    MissingFileExtensionError,
    UnsupportedFileExtensionError,
)
from ..icumf import ICUMF
from ..utils import _deep_merge
from .base_loader import BaseLoader

# ruff: noqa F401
from .json_loader import JsonLoader
from .xml_loader import XmlLoader
from .yaml_loader import YamlLoader

logger = logging.getLogger(__name__)


class Loader:
    """Loader class for loading locale files."""

    def __init__(self, strict: bool = False, icumf: Union[Optional[ICUMF], bool] = None):
        """Initialize the Loader class."""
        if icumf is None:
            icumf = ICUMF(strict)
        self.loaders = {ext: cls_loader(strict) for ext, cls_loader in BaseLoader._LOADERS.items()}
        self._logger = logger
        self._strict = strict
        self._icumf = icumf

    def get_supported_extensions(self) -> Tuple[str]:
        """Return a list of supported file extensions."""
        return tuple(self.loaders.keys())

    def load(self, filepath: Union[str, Path]) -> Union[Dict, List[Tuple[str, dict]]]:
        """
        Load the content of a file and processes it based on its extension.

        This method takes a file path as input, determines the file extension, and
        uses the associated loader to process the file content. If the file has no
        extension or the extension is unsupported, an exception is raised. If the file
        contains multiple locales, additional processing is performed.

        :param filepath: The path to the file to be loaded.
        :type filepath: str
        :return: The data loaded from the file; can be a dictionary or a list of
            tuples containing locale information.
        :rtype: Dict | List[Tuple[str, dict]]
        :raises MissingFileExtensionError: If the file does not have an extension.
        :raises UnsupportedFileExtensionError: If the file extension is not supported.
        """
        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1]
        if not extension:
            return self._throw(f"File '{filename}' has no extension", MissingFileExtensionError)

        if loader := self.loaders.get(extension.lower()):
            data: Union[dict[Any, Any], list[dict[Any, Any]]] = loader.load(filepath)
            if isinstance(data, list):
                locales = self._load_multiple_locales(filename, data)
                for _, locale in locales:
                    self._process_data(locale)

                return locales
            else:
                self._process_data(data)
                return data

        else:
            return self._throw(
                f"Unsupported file extension '{extension}' in '{filename}'. "
                f"doti18n supports: {self.get_supported_extensions()}",
                UnsupportedFileExtensionError,
            )

    def _process_data(self, data: Dict[Any, Any]):
        """Recursively process data to parse strings using ICUMF."""
        if not (isinstance(self._icumf, ICUMF)):
            return

        for key, value in data.items():
            if isinstance(value, dict):
                self._process_data(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._process_data(item)
                    elif isinstance(item, str):
                        processed_item = self._icumf.parse(item)
                        index = value.index(item)
                        value[index] = processed_item
            elif isinstance(value, str):
                processed_value = self._icumf.parse(value)
                data[key] = processed_value
            else:
                continue

    def _load_multiple_locales(self, filename: str, data: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Process and validate multiple locale configurations.

        :param filename: The name of the file containing the locale data.
        :type filename: str
        :param data: A list of documents, where each document is expected to represent locale data.
        :type data: list
        :return: A list of tuples containing locale code and corresponding locale data, or None if no valid
            locales are found.
        :rtype: Optional[List[Tuple[str, dict]]]
        :raises LocaleIdentifierMissingError: If a locale document is missing, the 'locale' key.
        :raises InvalidLocaleDocumentError: If a document is not a dictionary or no valid locales are found.
        """
        initial_data: Dict[str, Dict[str, Any]] = {}

        for index, document in enumerate(data):
            if not isinstance(document, dict):
                self._throw(
                    f"Locale document #{index} in '{filename}' is not a dictionary.", InvalidLocaleDocumentError
                )
                continue

            locale_code = document.get("locale", None)
            if not isinstance(locale_code, str):
                self._throw(
                    f"Locale document #{index} in '{filename}' is missing the 'locale' key.",
                    LocaleIdentifierMissingError,
                )
                continue

            content = document.copy()
            content.pop("locale")

            if locale_code not in initial_data:
                initial_data[locale_code] = {}

            _deep_merge(content, initial_data[locale_code])

        locales: List[Tuple[str, Dict[str, Any]]] = []
        for locale_code, locale_data in initial_data.items():
            self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
            locales.append((locale_code, locale_data))

        if not locales:
            self._throw(f"Locale file '{filename}' does not contain any valid locale data.", InvalidLocaleDocumentError)

        return locales

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> Dict:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
