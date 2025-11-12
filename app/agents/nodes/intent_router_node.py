import json
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.enums.ai_model import AiModel
from app.core.logger import get_logger
from app.enums.tool_call import toolcall

logger = get_logger("intent_router_node")
def intent_router_node(state: AgentState) -> Dict[str, Any]:

    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")
    system_prompt = PROMPTS.get("intent_router", query=user_message)
    logger.info(f"messages history: {len(conversation_history)}")

    messages = [
        SystemMessage(content=system_prompt),
        *conversation_history
    ]

    response = llm.invoke(messages)
    logger.info(f"Intent classification response: {response}")

    new_messages = [
        HumanMessage(content=user_message),
        AIMessage(content=response.content)
    ]

    try:
        result = json.loads(response.content)
        intent = result.get("intent", "other").strip().lower()
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        intent = "other"

    logger.info(f"[IntentClassifier] detected intent: {intent}")

    return {
        "intent": intent,
        "tool_call": toolcall.SQL_QUERY_GENERATE ,
        "response": result.get("reasoning", "other").strip().lower(),
        "messages": new_messages
    }