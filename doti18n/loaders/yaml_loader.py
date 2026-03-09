import logging
import os
from pathlib import Path
from typing import Dict, List, NoReturn, Optional, Union

from ..errors import EmptyFileError, ParseError
from ..utils import _get_locale_code
from .base_loader import BaseLoader

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

try:
    import ruamel.yaml as ryaml
except ImportError:
    ryaml = None  # type: ignore


class YamlLoader(BaseLoader):
    """Loader for YAML files."""

    file_extension = (".yaml", ".yml")

    def __init__(self, strict: bool = False):
        """Initialize the YamlLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict

    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """Load and validate localization data from a YAML file."""
        if not yaml:
            raise ImportError("PyYAML package is not installed, cannot load YAML files.")

        filename = os.path.basename(filepath)
        # noinspection PyUnresolvedReferences
        try:
            with open(filepath, encoding="utf-8") as f:
                locale_code = _get_locale_code(filename)
                # noinspection PyUnresolvedReferences
                data = list(yaml.safe_load_all(f))
                if not data:
                    return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

                if len(data) > 1:
                    return data

                else:
                    self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
                    return {locale_code: data[0]}

        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except yaml.YAMLError as e:
            self._throw(f"Error parsing YAML file '{filename}': {e}", ParseError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        return None

    def load_with_comments(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """Load a YAML file while preserving comments."""
        global yaml
        if not ryaml:
            raise ImportError("ruamel.yaml package is not installed, cannot load YAML files with comments.")

        if not yaml:
            raise ImportError("PyYAML package is not installed, cannot load YAML files.")

        _yaml = yaml
        try:
            yaml = ryaml.YAML(typ="rt")  # type: ignore
            yaml.safe_load_all = yaml.load_all  # type: ignore
            yaml.YAMLError = ryaml.YAMLError  # type: ignore
            data = self.load(filepath)
        finally:
            yaml = _yaml

        return data

    @staticmethod
    def save(filepath: Union[str, Path], data: Dict[str, Dict]):
        """Save localization data to a YAML file."""
        global yaml
        if not ryaml:
            raise ImportError("ruamel.yaml package is not installed, cannot save YAML files with comments.")

        if not yaml:
            raise ImportError("PyYAML package is not installed, cannot save YAML files.")

        _yaml = ryaml.YAML()
        with open(filepath, "w", encoding="utf-8") as f:
            _yaml.dump(data, f)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> Union[Dict, NoReturn]:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
