import json
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.db.dbconnection import get_table_info
from app.enums.ai_model import AiModel
from app.core.logger import get_logger
from app.enums.tool_call import toolcall

logger = get_logger("intent_router_node")
def intent_router_node(state: AgentState) -> Dict[str, Any]:

    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")
    db_schema = state.get("db_schema")
    schema_sent_once = state.get("schema_sent_once", False)

    if not db_schema or not schema_sent_once:
        try:
            db_schema = get_table_info()
            logger.info(f"Schema freshly loaded with {len(db_schema)} tables.")
            schema_sent_once = True
        except Exception as e:
            logger.error(f"sql_generator_tool failed to get db_schema: {e}")
            return {
                "db_schema": "",
                "response": f"sql_generator_tool failed to get db_schema: {e}",
                "schema_sent_once": False
            }

    if not state.get("schema_sent_once"):
        schema_text = json.dumps(db_schema, indent=2)
        system_prompt = PROMPTS.get("intent_router", query=user_message, db_schema=schema_text)
        logger.info("Sending full schema to GPT for the first time.")
    else:
        system_prompt = PROMPTS.get("intent_router", query=user_message,
                                    db_schema="(Schema already provided in context)")
        logger.info("Schema already known, sending prompt without full schema.")

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
        "messages": new_messages,
        "schema_sent_once": schema_sent_once,
        "db_schema": db_schema
    }