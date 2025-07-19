import logging
import os
import xml.etree.ElementTree as Et
from typing import Dict, List, NoReturn, Optional, Union

from ..errors import EmptyFileError, InvalidLocaleDocumentError, InvalidLocaleIdentifierError, ParseError
from ..utils import _get_locale_code
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)


class XmlLoader(BaseLoader):
    """Loader for XML files."""

    def __init__(self, strict: bool = False):
        """Initialize the XmlLoader class."""
        self._logger = logger
        self._strict = strict
        self.file_extension = ".xml"

    def load(self, filepath: str) -> Optional[Union[Dict, List[dict]]]:
        """
        Load and processes localization data from an XML file.

        The method supports both single and multiple locale documents.
        If the root element of the file matches predefined tags associated with multiple locales
        (such as "locales", "localizations", or "translations"),
        the data is processed into a list of dictionaries, each containing a locale code and its translations.
        Otherwise, the file is treated as a single locale document.
        The method ensures validation of loaded data and extracts locale codes based on filenames.

        :param filepath: The path to the XML localization file to be loaded.
        :type filepath: str
        :return: A dictionary with locale code and its translations for single locale
                 documents, or a list of dictionaries for multiple locale XML files.
                 Returns None if the file is determined to be empty or invalid.
        :rtype: Optional[Dict | List[dict]]
        :raises EmptyFileError: If the file is empty and contains no data.
        :raises InvalidLocaleDocumentError: If the data structure in the file does not
                 match the expected format.
        :raises ParseError: If the XML file cannot be parsed successfully due to syntax errors.
        :raises FileNotFoundError: If the specified file does not exist.
        :raises Exception: For any other unexpected errors encountered while loading files.
        """
        # note: ROOT ELEMENT IGNORED
        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                root = Et.fromstring(f.read())
                multiple = root.tag in ("locales", "localizations", "translations")
                data = self._etree_to_dict(root)
                if not data:
                    return self._throw(f"Locale file '{filename}' is empty", EmptyFileError)

            if multiple:
                proccessed = []
                for locale_code, translations in data.items():
                    if not isinstance(translations, dict):
                        return self._throw(
                            f"File '{filename}': locale '{locale_code}': data must be a dictionary, "
                            f"but got {type(translations).__name__}",
                            InvalidLocaleDocumentError,
                        )

                    self._validate(filepath, translations)
                    entry = {"locale": locale_code}
                    entry.update(translations)
                    proccessed.append(entry)

                return proccessed

            self._validate(filepath, data)
            locale_code = _get_locale_code(filename)
            self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
            return {locale_code: data}

        except Et.ParseError as e:
            self._throw(f"Error parsing XML file '{filename}': {e}", ParseError)
        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        return None

    def _etree_to_dict(self, node):
        if node.attrib.get("list") == "true":
            return [self._etree_to_dict(child) for child in node]

        if len(node) == 0:
            return node.text or ""

        result = {}
        for child in node:
            child_data = self._etree_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result

    def _validate(self, filepath: str, data: dict, path: Optional[List[str]] = None):
        path = path or []
        for key in data.keys():
            if not isinstance(key, str):
                self._throw(
                    f"XML key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if not key.isidentifier():
                self._throw(
                    f"XML key '{key}' is not a valid Python identifier. "
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
