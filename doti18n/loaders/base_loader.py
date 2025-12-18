from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union


class BaseLoader(ABC):
    """Base class for file loaders."""

    @abstractmethod
    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """Load and validate locale data from a file."""
        raise NotImplementedError
