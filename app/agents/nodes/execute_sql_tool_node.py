from typing import Dict, Any

from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query import execute_dynamic_sql_query
from app.core.logger import get_logger

logger = get_logger("sql_generator_node")


def execute_sql_tool_node(state: AgentState) -> Dict[str, Any]:
    sql = state.get("sql_query")

    if not sql:
        return {
            "response": "No SQL query was generated.",
            "tool_results": ""
        }

    result = execute_dynamic_sql_query.invoke({"sql_query": sql})

    if result["success"]:
        data = result.get("data", [])
        if not data:
            response_text = "Query ran successfully but returned no results."
        elif len(data) == 1:
            row = data[0]
            response_text = "Result:\n" + "\n".join(f"- {k}: {v}" for k, v in row.items())
        else:
            text = f"Found {len(data)} results (showing first 5):\n"
            for i, row in enumerate(data[:5], 1):
                text += f"\nResult {i}:\n" + "\n".join(f"  - {k}: {v}" for k, v in row.items())
            if len(data) > 5:
                text += f"\n...and {len(data) - 5} more results"
            response_text = text
    else:
        response_text = f"Error executing query: {result['error']}"

    logger.info(f"[execute_sql_tool_node] tool result: {response_text}")

    return {
        "response": response_text,
        "tool_results": result
    }