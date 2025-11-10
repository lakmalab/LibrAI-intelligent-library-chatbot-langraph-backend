import os
from functools import lru_cache
from .file_provider import FilePromptProvider

class PromptRegistry:
    def __init__(self, base_dir: str):
        self.provider = FilePromptProvider(os.path.join(base_dir, "templates"))

    @lru_cache(maxsize=None)
    def get(self, name: str, **kwargs) -> str:
        return self.provider.get_prompt(name, **kwargs)


PROMPTS = PromptRegistry(os.path.dirname(__file__))
