from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union


class BaseLoader(ABC):
    """Base class for file loaders."""

    _LOADERS: Dict = {}
    file_extension: Union[tuple, str]

    @abstractmethod
    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """Load and validate locale data from a file."""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """Register subclasses based on their file extensions."""
        super.__init_subclass__()

        if isinstance(cls.file_extension, (list, tuple, set)):
            for ext in cls.file_extension:
                cls._LOADERS[ext] = cls

        elif isinstance(cls.file_extension, str):
            cls._LOADERS[cls.file_extension] = cls
