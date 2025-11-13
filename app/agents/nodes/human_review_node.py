from typing import Dict, Any
import json

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.core.logger import get_logger
from app.enums import AiModel

logger = get_logger("human_review_node")
def human_review_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Human review node: Preparing SQL summary for review")

    sql_query = state.get("sql_query", "")
    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")
    system_prompt = PROMPTS.get("human_review", sql_query=sql_query, user_query=user_message)
    logger.info(f"messages history: {len(conversation_history)}")

    messages = [
        SystemMessage(content=system_prompt),
        *conversation_history
    ]

    response = llm.invoke(messages)
    logger.info(f"SQL summary response: {response}")

    review_message = {
        "summary": response.content,
        "status": "pending_review",
        "message": "Please review the summary of the SQL action before execution:",
        "requires_approval": True
    }
    logger.info(f"review_message: {review_message}")
    return {
        "pending_review": review_message,
        "awaiting_human_approval": True,
        "generated_sql_query": sql_query,
        "sql_reviewed": False,
        "sql_query": sql_query
    }
