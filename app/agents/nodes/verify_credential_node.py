import json
from typing import Dict, Any

from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query_tool import QueryExecutorTool

from app.core.logger import logger
from app.enums.intent import intents


def check_user_credentials_node(state: AgentState) -> Dict[str, Any]:
    logger.info(f"[check_user_credentials_node] called")

    user_email = state.get("user_email", "").strip()
    user_password = state.get("user_password", "").strip()

    if not user_email or not user_password:
        logger.info(f"[check_user_credentials_node] user_data: {user_email}, {user_password}")
        return {
            "sql_query": "",
            "intent": intents.CREDENTIALS_CHECK,
            "need_to_interrupt": True,
            "user_credentials_checked": True,
            "credentials_valid": False,
            "error": "Missing email or password",
            "user_data": {}
        }

    try:
        sql_query = f"SELECT id, name, email, membership_type FROM members WHERE email = '{user_email}' AND hashed_password = '{user_password}' AND is_active = true"

        query_tool = QueryExecutorTool()
        result = query_tool._run(sql_query)

        credentials_valid = result.get("success", False) and result.get("row_count", 0) > 0
        user_data = result.get("data", [{}])[0] if credentials_valid else {}
        logger.info(f"[check_user_credentials_node] user_data: {user_data}")
        return {
            "sql_query": sql_query,
            "intent": intents.CREDENTIALS_CHECK,
            "need_to_interrupt": not credentials_valid,
            "user_credentials_checked": True,
            "credentials_valid": credentials_valid,
            "user_data": user_data,
            "query_result": result
        }

    except Exception as e:
        logger.error(f"[check_user_credentials_node] Error: {str(e)}")
        return {
            "sql_query": "",
            "intent": intents.CREDENTIALS_CHECK,
            "need_to_interrupt": True,
            "user_credentials_checked": True,
            "credentials_valid": False,
            "error": f"Database error: {str(e)}",
            "user_data": {}
        }