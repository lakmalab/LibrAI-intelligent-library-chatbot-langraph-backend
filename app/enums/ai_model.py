from enum import Enum

class AiModel(str, Enum):
    GPT_5_NANO = "gpt-5-nano"
    LLAMA3_2 = "llama3.2"
    GEMMA3 = "gemma3:1b"
