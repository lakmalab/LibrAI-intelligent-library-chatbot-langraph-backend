from typing import Dict, Any
from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query_tool import QueryExecutorTool
from app.enums.intent import intents


class ExecuteSQLQueryNode:
    def __init__(self):
        pass

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        sql_query = state.get("sql_query", "")

        if not sql_query:
            return {
                "tool_results": "No SQL query provided",
                "current_node": "ExecuteSQLQueryNode",
                **state,
            }

        query_tool = QueryExecutorTool()
        result = query_tool._run(sql_query)

        return {
            "tool_results": str(result),
            "intent": intents.SQL_QUERY,
            "current_node": "ExecuteSQLQueryNode"
        }