from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union


class BaseLoader(ABC):
    """Base class for file loaders."""

    _LOADERS: Dict = {}
    file_extension: Union[tuple, str]

    @abstractmethod
    def load(self, filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load and validate locale data from a file."""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """Register subclasses based on their file extensions."""
        super.__init_subclass__()
        cls._LOADERS[cls.file_extension] = cls
