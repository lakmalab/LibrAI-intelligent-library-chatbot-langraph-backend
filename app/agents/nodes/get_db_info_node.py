from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.tools.schema_search_tool import AgenticSchemaSearchTool
from app.enums import AiModel
from app.agents.llm_provider import get_llm
from app.core.logger import get_logger
from app.agents.state import AgentState

logger = get_logger("get_table_info_node")


def get_table_info_node(state: AgentState) -> Dict[str, Any]:

    logger.info("get_table_info_node called")

    user_query = state.get("user_query", "")
    conversation_history = state.get("messages", [])

    tool = AgenticSchemaSearchTool()
    schema_result = tool.run(user_query)

    can_answer = schema_result.get("can_answer_query", False)
    validation = schema_result.get("validation", {})

    logger.info(f"Schema search complete: can_answer={can_answer}")
    logger.info(
        f"Tables analyzed: {schema_result.get('tables_analyzed', 0)} out of {schema_result.get('total_tables_in_db', 0)}")

    if not can_answer:
        logger.info("Query cannot be answered from database schema")
        return {
            "messages": conversation_history,
            "schema_info": schema_result,
            "can_answer_from_db": False,
            "assistant_response": (
                f"I searched the database but couldn't find relevant tables to answer your query. "
                f"Reason: {validation.get('reasoning', 'No matching schema found.')}"
            ),
        }

    llm = get_llm(model=AiModel.GPT_5_NANO, temperature=0)

    schema_summary = {
        "tables": [s["table"] for s in schema_result.get("schema", [])],
        "suggested_columns": validation.get("suggested_columns", []),
        "needs_joins": validation.get("needs_joins", False),
        "detailed_schema": schema_result.get("schema", [])
    }

    context_message = f"""Database Schema Analysis:

User Query: "{user_query}"

Relevant Tables Found: {', '.join(schema_summary['tables'])}

Schema Details:
{schema_result.get('schema', [])}

Validation:
- Can answer: {validation.get('can_answer', False)}
- Reasoning: {validation.get('reasoning', '')}
- Suggested tables: {validation.get('suggested_tables', [])}
- Needs joins: {validation.get('needs_joins', False)}

Based on this schema, the query can be answered from the database."""

    messages = [
        *conversation_history,
        HumanMessage(content=context_message)
    ]

    llm_response = llm.invoke(messages)

    conversation_history.append(HumanMessage(content=user_query))
    conversation_history.append(AIMessage(content=llm_response.content))

    return {
        "messages": conversation_history,
        "schema_info": schema_result,
        "can_answer_from_db": True,
        "assistant_response": llm_response.content,
        "sql_context": schema_summary
    }