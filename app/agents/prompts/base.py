from abc import ABC, abstractmethod
from typing import Any

class PromptProvider(ABC):

    @abstractmethod
    def get_prompt(self, name: str, **kwargs: Any) -> str:
        pass
