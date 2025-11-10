import os
from jinja2 import Environment, FileSystemLoader
from .base import PromptProvider

class FilePromptProvider(PromptProvider):
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def get_prompt(self, name: str, **kwargs) -> str:
        for ext in (".txt", ".j2"):
            path = os.path.join(self.template_dir, name + ext)
            if os.path.exists(path):
                template = self.env.get_template(name + ext)
                return template.render(**kwargs)
        raise FileNotFoundError(f"Prompt '{name}' not found in {self.template_dir}")
