from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseLoader(ABC):
    """Base class for file loaders."""

    _LOADERS: dict = {}
    file_extension: tuple[str, ...] | str

    @abstractmethod
    def load(self, filepath: str | Path) -> dict[str, Any]:
        """Load and validate locale data from a file."""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """Register subclasses based on their file extensions."""
        super.__init_subclass__()
        cls._LOADERS[cls.file_extension] = cls
