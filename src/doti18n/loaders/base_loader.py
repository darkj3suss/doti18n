from abc import ABC, abstractmethod
from typing import (
    Optional,
    Dict,
    Any,
    List
)


class BaseLoader(ABC):
    @abstractmethod
    def load(self, filepath: str, ignore_warnings: bool = False) -> Optional[Dict[str, Any] | List[dict]]:
        raise NotImplementedError
