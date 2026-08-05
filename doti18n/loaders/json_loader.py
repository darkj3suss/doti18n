import json
import logging
import os
from pathlib import Path
from typing import Any, NoReturn

from ..errors import (
    EmptyFileError,
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

    def load(self, filepath: str | Path) -> dict[str, Any]:
        """Load locale data from a JSON file."""
        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            self._throw(f"Error parsing JSON file '{filename}': {e}", ParseError)
        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        if not data:
            self._throw(f"Locale file '{filename}' is empty", EmptyFileError)
            return {}

        locale_code = _get_locale_code(filename)
        self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
        return {locale_code: data}

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> dict | NoReturn:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
