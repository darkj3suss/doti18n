import os

import yaml
import logging
from .base_loader import BaseLoader
from ..utils import (
    _get_locale_code,
    _EMPTY_FILE
)
from typing import (
    Optional,
    List,
    Tuple,
    Dict,
    Any
)

logger = logging.getLogger(__name__)


class YamlLoader(BaseLoader):
    def __init__(self, strict: bool = False):
        self._logger = logger
        self._strict = strict
        self.file_extension = (".yaml", ".yml")

    def load(self, filepath: str, ignore_warnings: bool = False) -> Optional[Dict[str, Any] | List[dict]]:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, encoding='utf-8') as f:
                locale_code = _get_locale_code(filename)
                data = list(yaml.safe_load_all(f))
                if not data:
                    if not ignore_warnings:
                        self._logger.warning(f"Locale file '{filename}' is empty")

                    return _EMPTY_FILE

                if len(data) > 1:
                    return data

                else:
                    self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
                    return {locale_code: data[0]}

        except FileNotFoundError:
            if not ignore_warnings:
                self._logger.error(f"Locale file '{filename}' not found during load.")
        except yaml.YAMLError as e:
            if not ignore_warnings:
                self._logger.error(f"Error parsing YAML file '{filename}': {e}")
        except Exception as e:
            if not ignore_warnings:
                self._logger.error(f"Unknown error loading '{filename}': {e}", exc_info=True)
