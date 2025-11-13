import json
import uuid
from typing import Dict, Any, List

from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.tools import BaseTool

from app.agents.state import AgentState
from app.core.logger import logger
from app.enums.tool_call import toolcall


class ToolCallerNode:
    def __init__(self, tools: List[BaseTool]):
        self.tool_map = {tool.name: tool for tool in tools}

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        current_tool_call = state.get("tool_call")
        logger.info(f"ToolCallerNode: {current_tool_call}")
        results = {}
        tool_messages = []

        if current_tool_call == toolcall.SQL_QUERY_GENERATE:
            try:
                if "sql_generator" in self.tool_map:
                    user_query = state.get("user_query", "")

                    tool_result = self.tool_map["sql_generator"].invoke({
                        "state": state,
                        "user_query": user_query
                    })

                    results["sql_query"] = tool_result.get("sql_query", "")
                    results["tool_call"] = toolcall.SQL_QUERY_EXECUTE
                    results["db_schema"] = tool_result.get("db_schema")
                    results["schema_sent_once"] = tool_result.get("schema_sent_once", True)

                    tool_content = json.dumps(tool_result, default=str)
                    tool_call_id = str(uuid.uuid4())
                    tool_messages.append(ToolMessage(
                        content=tool_content,
                        tool_call_id=tool_call_id,
                        name="sql_generator"
                    ))
                    tool_messages.append(AIMessage(content=tool_result.get("sql_query", "")))

            except Exception as e:
                error_msg = f"Error executing SQL generator: {str(e)}"
                tool_messages.append(ToolMessage(
                    content=error_msg,
                    tool_call_id=str(uuid.uuid4()),
                    name="sql_generator"
                ))
                tool_messages.append(AIMessage(content=error_msg))
                results["error"] = error_msg

        elif current_tool_call == toolcall.SQL_QUERY_EXECUTE:
            try:
                if "query_executor" in self.tool_map:
                    sql_query = state.get("sql_query", "")
                    if not sql_query:
                        raise ValueError("No SQL query found to execute")

                    tool_result = self.tool_map["query_executor"].invoke(sql_query)

                    results["query_results"] = tool_result
                    results["tool_call"] = ""
                    results["sql_approved"] = False
                    results["sql_reviewed"] = False
                    results["awaiting_human_approval"] = False
                    results["tool_results"] = json.dumps(tool_result, default=str)

            except Exception as e:
                error_msg = f"Error executing SQL query: {str(e)}"
                tool_messages.append(ToolMessage(
                    content=error_msg,
                    name="query_executor",
                    tool_call_id=str(uuid.uuid4())
                ))
                tool_messages.append(AIMessage(content=error_msg))
                results["error"] = error_msg

        return {
            "response": tool_messages,
            **results
        }
