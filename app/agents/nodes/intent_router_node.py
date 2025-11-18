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

    schema_info = state.get("schema_info","")


    schema_matches = schema_info.get("schema", "")
    #logger.info(f"schema_info: {schema_matches}")
    #logger.info(f"Schema matches found: {schema_matches}")

    if schema_matches and len(schema_matches) > 0:
        logger.info("Intent resolved instantly: SQL QUERY (tables matched)")
        return {
            "intent": "sql_query",
            "response": "Relevant table(s) found in schema → SQL query.",
            "messages": [
                HumanMessage(content=user_message),
                AIMessage(content="Detected SQL intent based on schema match.")
            ],
            "schema_info": schema_info
        }


    system_prompt = PROMPTS.get(
        "intent_router",
        query=user_message,
        db_schema="(Schema not used; no table matches)"
    )

    messages = [
        SystemMessage(content=system_prompt),
        *conversation_history
    ]

    logger.info("Calling LLM for intent classification…")
    response = llm.invoke(messages)

    try:
        result = json.loads(response.content)
        intent = result.get("intent", "other").strip().lower()
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        intent = "general_chat"
        result = {"intent": "general_chat", "reasoning": "fallback"}

    logger.info(f"[IntentClassifier] detected intent: {intent}")

    new_messages = [
        HumanMessage(content=user_message),
        AIMessage(content=response.content)
    ]

    return {
        "intent": intent,
        "response": result.get("reasoning", ""),
        "messages": new_messages,
        "schema_info": schema_info
    }
