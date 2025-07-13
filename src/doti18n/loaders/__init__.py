import logging
import os
from typing import (
    Optional,
    List,
    Tuple, Dict
)

from .yaml_loader import YamlLoader
from .json_loader import JsonLoader
from ..utils import (
    _deep_merge,
    _EMPTY_FILE,
)


logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, strict: bool = False):
        self._logger = logger
        self._strict = strict
        self._LOADERS = (
            YamlLoader(strict),
            JsonLoader(strict)
        )
        self.SUPPORTED_EXTENSIONS = self._get_supported_extensions()

    def _get_supported_extensions(self):
        result = []
        for loader in self._LOADERS:
            if type(loader.file_extension) is str:
                result.append(loader.file_extension)
            else:
                result.extend(loader.file_extension)

        return result

    def load(self, filepath: str) -> Optional[Dict | List[Tuple[str, dict]]]:
        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1]
        if extension:
            for loader in self._LOADERS:
                if extension in loader.file_extension:
                    data = loader.load(filepath)
                    if isinstance(data, list):
                        return self.load_multiple_locales(filename, data)
                    elif isinstance(data, dict):
                        return data
                    elif data is _EMPTY_FILE:
                        return None
                    elif data is None:
                        return None
            else:
                msg = f"Unsupported file extension '{extension}' in '{filename}'"
                if self._strict:
                    raise ValueError(msg)
                else:
                    self._logger.warning(msg)
                    return None
        else:
            if self._strict:
                raise ValueError(f"File '{filename}' has no extension")
            else:
                logger.info(f"File '{filename}' has no extension, trying to guess it...")
                return self.guess_filetype(filepath)

    def guess_filetype(self, filepath: str) -> Optional[tuple[str, dict] | list[tuple[str, dict]]]:
        filename = os.path.basename(filepath)
        locale_code = None
        for loader in self._LOADERS:
            data = loader.load(filepath, ignore_warnings=True)
            if not data:
                return None

            if data is _EMPTY_FILE:
                self._logger.warning(
                    f"Locale file '{filename}' loaded using {loader.__class__.__name__} "
                    f"and was classified as empty"
                )
                return None

            if isinstance(data, list):
                data = self.load_multiple_locales(filename, data)
                locale_code = "; ".join([f"'{dct[0]}'" for dct in data])

            elif isinstance(data, dict):
                locale_code = list(data.keys())[0]

            if locale_code:
                self._logger.info(
                    f"Loaded locale data, using {loader.__class__.__name__} "
                    f"locale_code: '{locale_code}' from file '{filename}'"
                )
                return data

        logger.warning(f"Unable to guess file type for file '{filename}'")
        return None

    def load_multiple_locales(self, filename: str, data: list) -> Optional[List[Tuple[str, dict]]]:
        result = {}
        for index, document in enumerate(data):
            if not document:
                logger.warning(f"Empty document {index + 1} in locale file '{filename}'. Skipping...")
                continue

            if isinstance(document, dict):
                locale_code = document.get('locale', None)
                if not locale_code:
                    self._logger.warning(
                        f"Locale code not found in locale file '{filename}', document {index + 1}. Skipping...\n"
                        f"If you want use one file for multiple locales - add a 'locale' key to the document."
                    )
                    continue

                document.pop("locale")
                if result.get(locale_code):
                    _deep_merge(document, result[locale_code])
                else:
                    result[locale_code] = document

        locales = []
        for locale_code, data in result.items():
            self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
            locales.append((locale_code, data))

        if not locales:
            logger.warning(f"No locale data found in locale file '{filename}'.")
            return None

        return locales
