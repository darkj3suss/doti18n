import logging
import os
from pathlib import Path
from typing import Dict, List, NoReturn, Optional, Union

from ..errors import EmptyFileError, InvalidLocaleIdentifierError, ParseError
from ..utils import _get_locale_code
from .base_loader import BaseLoader

try:
    import yaml

    _yaml_available = True
except ImportError:
    _yaml_available = False


logger = logging.getLogger(__name__)


class YamlLoader(BaseLoader):
    """Loader for YAML files."""
    file_extension = (".yaml", ".yml")

    def __init__(self, strict: bool = False):
        """Initialize the YamlLoader class."""
        self._logger = logger
        self._strict = strict

    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """
        Load and validate localization data from a YAML file.

        Supports files containing either a single YAML document or multiple documents.
        For single-document YAML files, the document is returned as a dictionary mapped to the locale code.
        For multi-document YAML files, a list of dictionaries is returned. Errors are handled
        and parsed in cases such as missing files, malformed YAML syntax, or other exceptions.

        :param filepath: The full path to the YAML file to load.
        :return: A dictionary containing locale-specific data if a single document is found.
            For multi-document files, a list of dictionaries is returned. If the file is empty,
            an empty dictionary is returned.
        :raises ImportError: If the PyYAML package is not installed.
        :raises FileNotFoundError: If the specified file does not exist.
        :raises ParseError: For issues in parsing the YAML file.
        :raises Exception: For any other unexpected exceptions during the load process.
        """
        if not _yaml_available:
            raise ImportError("PyYAML package is not installed, cannot load YAML files.")

        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                locale_code = _get_locale_code(filename)
                data = list(yaml.safe_load_all(f))
                if not data:
                    return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

                if len(data) > 1:
                    for locale in data:
                        self._validate(filepath, locale)

                    return data

                else:
                    self._validate(filepath, data[0])
                    self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
                    return {locale_code: data[0]}

        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except yaml.YAMLError as e:
            self._throw(f"Error parsing YAML file '{filename}': {e}", ParseError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        return None

    def _validate(self, filepath: str, data: dict, path: Optional[List[str]] = None):
        path = path or []
        for key in data.keys():
            if not isinstance(key, str):
                self._throw(
                    f"YAML key '{key}' is not a valid Python identifier. "
                    f"Problem found at path: '{':'.join(map(str, path + [key]))}' "
                    f"in file: {filepath}",
                    InvalidLocaleIdentifierError,
                )

            if not key.isidentifier():
                self._throw(
                    f"YAML key '{key}' is not a valid Python identifier. "
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
