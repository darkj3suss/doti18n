import logging
import os
from pathlib import Path
from typing import Any, NoReturn

from ..errors import EmptyFileError, ParseError
from ..utils import _get_locale_code
from .base_loader import BaseLoader

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


class YamlLoader(BaseLoader):
    """Loader for YAML files."""

    file_extension = (".yaml", ".yml")

    def __init__(self, strict: bool = False):
        """Initialize the YamlLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict

    def load(self, filepath: str | Path) -> dict[str, Any]:
        """Load and validate localization data from a YAML file."""
        if not yaml:
            raise ImportError("PyYAML package is not installed, cannot load YAML files.")

        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                locale_code = _get_locale_code(filename)
                data = list(yaml.safe_load_all(f))

        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except yaml.YAMLError as e:
            self._throw(f"Error parsing YAML file '{filename}': {e}", ParseError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        if not data:
            return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

        self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
        if len(data) == 1:
            data = data[0]

        return {locale_code: data}

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> dict | NoReturn:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
