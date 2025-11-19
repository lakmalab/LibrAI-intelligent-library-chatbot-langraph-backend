from typing import Dict, Any
import json

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.core.logger import get_logger
from app.enums import AiModel

logger = get_logger("credential_review_node")


def credential_review_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Credential review node: Preparing credential summary for human approval")

    email = state.get("user_email", "lakmal")
    password = state.get("user_password", "12345")
    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")

    system_prompt = PROMPTS.get("credential_review").format(
        email=email,
        password=password,
        user_query=user_message
    )

    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    messages = [
        SystemMessage(content=system_prompt),
        *conversation_history
    ]

    response = llm.invoke(messages)

    review_message = {
        "summary": response.content,
        "status": "pending_credential_confirmation",
        "message": "Please confirm the email and password before continuing:",
        "requires_approval": True
    }
    logger.info(f"review_message:{review_message}", )
    return {
        "pending_review": review_message,
        "awaiting_credential_approval": True,
        "user_email": email,
        "user_password": password,
        "credentials_reviewed": False
    }
