from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.enums import AiModel
from app.core.logger import get_logger
import json

from app.enums.intent import intents

logger = get_logger("conversational_response_node")


class GenerateConversationalResponseNode:
    def __init__(self):
        pass

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        intent = state.get("intent")
        logger.info(f"Intent received: {intent}")
        llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

        conversation_history = state.get("messages", [])
        user_message = state.get("user_query", "")

        if intent == intents.GENERAL:
            #llm = get_llm(temperature=0, model=AiModel.GEMMA3)
            system_prompt = PROMPTS.get("general_chat").format(
                query=user_message
            )
            messages = [
                SystemMessage(content=system_prompt),
                *conversation_history
            ]

            response = llm.invoke(messages)
            logger.info(f"IGeneral chat response: {response}")

        elif intent == intents.SQL_QUERY:
            query_result = state.get("tool_results")
            query_result_text = json.dumps(query_result, indent=2)
            if query_result:
                system_prompt = PROMPTS.get("sql_result_natural").format(
                    query=user_message,
                    query_result=query_result_text
                )
                messages = [
                    SystemMessage(content=system_prompt),
                    *conversation_history
                ]

                response = llm.invoke(messages)
                logger.info(f"sql_result_natural chat response: {response}")
            else:
                response = "something went wrong getting the sql results"

        elif intent == intents.REJECTED:
            query_result = state.get("tool_results")
            query_result_text = json.dumps(query_result, indent=2)
            if query_result:
                system_prompt = PROMPTS.get("sql_rejected").format(
                    user_query=user_message,
                    sql_query=query_result_text
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    *conversation_history
                ]
                logger.error(f"sql_result_natural chat response: {messages}")
                response = llm.invoke(messages)
                logger.info(f"sql_result_natural chat response: {response}")
            else:
                response = "something went wrong getting the sql results"

        else:
            system_prompt = PROMPTS.get("fallback").format(
                query=user_message
            )
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
            "messages": new_messages,
            "current_node": "GenerateConversationalResponseNode"
        }