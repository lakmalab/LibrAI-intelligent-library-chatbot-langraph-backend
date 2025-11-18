from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query_tool import QueryExecutorTool
from app.enums.intent import intents


def execute_sql_query_node(state: AgentState) -> AgentState:
    sql_query = state.get("sql_query", "")

    if not sql_query:
        state["tool_results"] = "No SQL query provided"
        return state

    query_tool = QueryExecutorTool()

    result = query_tool._run(sql_query)

    state["tool_results"] = str(result)
    state["intent"] = intents.SQL_QUERY
    return state
