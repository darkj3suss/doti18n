import logging
import os
from pathlib import Path
from typing import Any, NoReturn

from ..errors import EmptyFileError, ParseError
from ..utils import _get_locale_code
from .base_loader import BaseLoader

try:
    import tomllib
except ImportError:
    # tomllib is in stdlib since Python 3.11
    tomllib = None  # type: ignore

try:
    import tomlkit
    import tomlkit.exceptions as err
except ImportError:
    tomlkit = None  # type: ignore
    err = None  # type: ignore


class TomlLoader(BaseLoader):
    """Loader for TOML files."""

    file_extension = ".toml"

    def __init__(self, strict: bool = False):
        """Initialize the TomlLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict

    def load(self, filepath: str | Path) -> dict[str, Any]:
        """Load and validate localization data from a TOML file."""
        if not tomllib:
            raise ImportError("tomllib is not available. TOML support requires Python 3.11+.")

        filename = os.path.basename(filepath)
        try:
            with open(filepath, "rb") as f:
                data = tomllib.load(f)

        except FileNotFoundError:
            self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except tomllib.TOMLDecodeError as e:
            self._throw(f"Error parsing TOML file '{filename}': {e}", ParseError)
        except Exception as e:
            self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        if not data:
            return self._throw(f"Locale file '{filename}' is empty.", EmptyFileError)

        locale_code = _get_locale_code(filename)
        self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
        return {locale_code: data}

    def load_with_comments(self, filepath: str | Path) -> dict | list[dict]:
        """Load and validate localization data from a TOML file, preserving comments."""
        global tomllib, tomlkit
        if not tomlkit:
            raise ImportError("tomlkit is not available. Comment support for TOML files requires the tomlkit package.")

        if not tomllib:
            raise ImportError("tomllib is not available. TOML support requires Python 3.11+.")

        _tomltib = tomllib  # type: ignore
        try:
            tomlib = tomlkit  # type: ignore
            tomlib.TOMLDecodeError = err.ParseError  # type: ignore
            data = self.load(filepath)
        finally:
            tomlib = _tomltib  # type: ignore

        return data

    @staticmethod
    def save(filepath: str | Path, data: dict[str, dict]):
        """Save localization data to a TOML file."""
        if not tomlkit:
            raise ImportError("tomlkit is not available. Saving TOML files with comments requires the tomlkit package.")

        with open(filepath, "w", encoding="utf-8") as f:
            toml_string = tomlkit.dumps(data)  # type: ignore
            f.write(toml_string)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> dict | NoReturn:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
