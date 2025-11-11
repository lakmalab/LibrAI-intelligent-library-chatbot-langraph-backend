from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.enums import AiModel
from app.core.logger import get_logger
import json

logger = get_logger("conversational_response_node")
def generate_conversational_response(state: AgentState) -> Dict[str, Any]:
    intent = state.get("intent")
    logger.info(f"Intent received: {intent}")
    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")


    if intent == "general_chat":
        system_prompt = PROMPTS.get("general_chat").format(
            query=user_message
        )
        messages = [
            SystemMessage(content=system_prompt),
            *conversation_history
        ]

        response = llm.invoke(messages)
        logger.info(f"IGeneral chat response: {response}")


    elif intent == "sql_query":
        query_result = state.get("tool_results")
        query_result_text = json.dumps(query_result, indent=2)
        if query_result:
            system_prompt = PROMPTS.get("sql_result_natural").format(
                query=user_message,
                query_result=query_result_text
            )
            logger.info(f"system_prompt: {system_prompt}")
            messages = [
                SystemMessage(content=system_prompt),
                *conversation_history
            ]

            response = llm.invoke(messages)
            logger.info(f"sql_result_natural chat response: {response}")
        else:
            response ="something went wrong getting the sql results"

    else:
        system_prompt = """You are a friendly library assistant chatbot.
                        The user's intent is unclear. Respond naturally and try to understand what they need.
                        Ask clarifying questions if needed, or offer general assistance.
                        Be helpful, friendly, and guide them toward the information or service they might need."""

        messages = [
            SystemMessage(content=system_prompt),
            *conversation_history
        ]

        response = llm.invoke(messages)
        logger.info(f"Fallback response generated for unknown intent")

    logger.info(f"Generated response: {response.content[:100]}...")

    new_messages = [
        HumanMessage(content=user_message),
        AIMessage(content=response.content)
    ]

    return {
        "response": response.content.strip(),
        "messages": new_messages
    }