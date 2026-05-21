import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

from ..errors import (
    InvalidLocaleDocumentError,
    MissingFileExtensionError,
    UnsupportedFileExtensionError,
)
from ..icumf import ICUMF
from .base_loader import BaseLoader

# ruff: noqa F401
from .json_loader import JsonLoader
from .xml_loader import XmlLoader
from .yaml_loader import YamlLoader
from .toml_loader import TomlLoader

logger = logging.getLogger(__name__)


class Loader:
    """Loader class for loading locale files."""

    def __init__(self, strict: bool = False, icumf: Union[Optional[ICUMF], bool] = None):
        """Initialize the Loader class."""
        if icumf is None:
            icumf = ICUMF(strict)
        self.loaders = {}
        for extension, loader_cls in BaseLoader._LOADERS.items():
            loader = loader_cls(strict)
            if isinstance(extension, (list, set, tuple)):
                for ext in extension:
                    self.loaders[ext] = loader
            elif isinstance(extension, str):
                self.loaders[extension] = loader
            else:
                raise ValueError(f"Invalid file extension type: {type(extension)} for loader {loader_cls.__name__}")

        self._logger = logger
        self._strict = strict
        self._icumf = icumf

    def get_supported_extensions(self) -> Tuple[str]:
        """Return a list of supported file extensions."""
        return tuple(self.loaders.keys())

    def load(self, filepath: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
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
            data: Dict[str, Any] = loader.load(filepath)
            for _, locale in data.items():
                if isinstance(locale, list):
                    for item in locale:
                        self._validate(filepath, item)
                        self._process_data(item)
                elif isinstance(locale, dict):
                    self._validate(filepath, locale)
                    self._process_data(locale)
                else:
                    self._throw(
                        f"Locale data in '{filename}' should be a dictionary or a list of dictionaries, "
                        f"but got {type(locale).__name__}",
                        InvalidLocaleDocumentError,
                    )

            return data

        else:
            return self._throw(
                f"Unsupported file extension '{extension}' in '{filename}'. "
                f"doti18n supports: {self.get_supported_extensions()}",
                UnsupportedFileExtensionError,
            )

    def _validate(self, filepath: Union[str, Path], data: dict | list, path: Optional[List[str | int]] = None):
        path = path or []
        if isinstance(data, dict):
            for key in data.keys():
                if not isinstance(key, str) or not key.isidentifier():
                    self._logger.warning(
                        f"Key '{key}' is not a valid Python identifier. Call via dot notation is not possible. "
                        f"Problem found at path: '{'.'.join(map(str, path + [key]))}' "
                        f"in file: {filepath}",
                    )

                if isinstance(data[key], dict):
                    self._validate(filepath, data[key], path + [key])

        elif isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._validate(filepath, item, path + [index])

    def _process_icumf(self, data: Dict[Any, Any]):
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

    @staticmethod
    def _process_macros(data_: Dict[Any, Any]):
        """Process macros in the data."""
        keys = ["__macros__"]
        for key in keys:
            if macros := data_.get(key, None):
                break
        else:
            return

        def replace_macros(data: Dict[Any, Any]) -> Any:
            nonlocal macros
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str):
                        data[k] = replace_macros(data[k])
                    else:
                        replace_macros(v)

            elif isinstance(data, list):
                for index, item in enumerate(data):
                    if isinstance(item, str):
                        data[index] = replace_macros(data[index])
                    else:
                        replace_macros(item)

            elif isinstance(data, str):
                if "@" not in data:
                    return data

                for macro_key, macro_value in macros.items():
                    if f"@{macro_key}" in data:
                        data = data.replace(f"@{macro_key}", macro_value)

                return data

            else:
                # just in case
                return data

        replace_macros(data_)

    def _process_data(self, data: Dict[Any, Any]):
        """Post-process loaded data."""
        self._process_macros(data)
        self._process_icumf(data)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> Dict:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
