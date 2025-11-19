from typing import Dict, Any

from app.agents.tools.schema_search_tool import AgenticSchemaSearchTool
from app.core.logger import get_logger
from app.agents.state import AgentState
from app.enums.intent import intents

logger = get_logger("get_table_info_node")


def get_table_info_node(state: AgentState) -> Dict[str, Any]:

    logger.info("get_table_info_node called")

    user_query = state.get("user_query", "")
    conversation_history = state.get("messages", [])

    user_email = state.get("user_email", "").strip()
    user_password = state.get("user_password", "").strip()
    logger.info(f"Schema search complete: can_answer={user_email}")
    tool = AgenticSchemaSearchTool()
    schema_result = tool.run({
        "query": user_query,
        "user_email": user_email,
        "user_password": user_password,
    })

    can_answer = schema_result.get("can_answer_query", False)
    need_to_interrupt = schema_result.get("need_to_interrupt", False)
    logger.info(f"Schema search complete: can_answer={can_answer}")
    logger.info(
        f"Tables analyzed: {schema_result.get('tables_analyzed', 0)} out of {schema_result.get('total_tables_in_db', 0)}")

    if not can_answer:
        logger.info("Query cannot be answered from database schema")
        return {
            "messages": conversation_history,
            "schema_info": schema_result,
            "can_answer_from_db": False,
            "need_to_interrupt": need_to_interrupt,
        }

    return {
        "messages": conversation_history,
        "schema_info": schema_result,
        "intent": intents.GENERAL,
        "can_answer_from_db": True,
        "need_to_interrupt": need_to_interrupt,
    }