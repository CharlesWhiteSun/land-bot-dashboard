from abc import ABC, abstractmethod
from typing import Dict

class ErrorProviderInterface(ABC):
    @abstractmethod
    def get_error(self, code: str) -> Dict[str, str]:
        pass
