import os

import json
import logging
from .base_loader import BaseLoader
from ..utils import (
    _get_locale_code,
    _EMPTY_FILE
)
from typing import (
    Optional,
    List,
    Dict,
    Any
)


logger = logging.getLogger(__name__)


class JsonLoader(BaseLoader):
    def __init__(self, strict: bool = False):
        self._logger = logger
        self._strict = strict
        self.file_extension = ".json"

    def load(self, filepath: str, ignore_warnings: bool = False) -> Optional[Dict[str, Any] | List[dict]]:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    if not ignore_warnings:
                        self._logger.warning(f"Locale file '{filename}' is empty")

                    return _EMPTY_FILE

                if isinstance(data, list):
                    return data

                locale_code = _get_locale_code(filename)
                return {locale_code: data}
        except json.decoder.JSONDecodeError:
            if not ignore_warnings:
                self._logger.error(f"Error parsing JSON file '{filename}'")
        except FileNotFoundError:
            if not ignore_warnings:
                self._logger.error(f"Locale file '{filename}' not found during load.")
        except Exception as e:
            if not ignore_warnings:
                self._logger.error(f"Unknown error loading '{filename}': {e}", exc_info=True)
