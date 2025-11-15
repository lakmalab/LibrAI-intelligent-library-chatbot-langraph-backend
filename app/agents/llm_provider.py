from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.enums import AiModel

def get_llm(temperature: float = 0, model: AiModel = AiModel.GPT_5_NANO):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")

        if model == AiModel.GPT_5_NANO:
            return ChatOpenAI(
                model= model,
                temperature=temperature,
                openai_api_key=settings.OPENAI_API_KEY
            )

        elif model == AiModel.GEMMA3:
            return ChatOllama (
                model=model,
                temperature=temperature
            )