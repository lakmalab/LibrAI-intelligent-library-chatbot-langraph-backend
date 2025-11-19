import json
from typing import Dict, Any

from app.agents.state import AgentState
from app.agents.tools.sql_generator_tool import SQLGeneratorTool
from app.core.logger import logger
from app.enums.intent import intents


def generate_sql_query_node(state: AgentState) -> Dict[str, Any]:
    logger.info(f"[generate_sql_query_node] called")
    sql_tool = SQLGeneratorTool()

    user_query = state.get("user_query", "")
    schema_info = state.get("schema_info", "")
    messages = state.get("messages", [])

    result = sql_tool._run(
        user_query=user_query,
        schema_info=schema_info,
        messages=messages
    )
    if isinstance(result, dict):
        result = json.dumps(result)

    new_state = state.copy()
    new_state.update({
        "sql_query": result
    })

    return {
        "sql_query": result,
        "intent": intents.SQL_QUERY,
        "need_to_interrupt": False
    }