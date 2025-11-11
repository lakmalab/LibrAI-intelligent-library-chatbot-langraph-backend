import json
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

from app.agents import prompt_templates
from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.agents.state import AgentState
from app.db.dbconnection import get_table_info
from app.enums.ai_model import AiModel
from app.core.logger import get_logger

logger = get_logger("sql_generator_node")


def sql_generator_node(state: AgentState) -> Dict[str, Any]:
    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")
    db_schema = state.get("db_schema")

    schema_freshly_loaded = False

    if not db_schema:
        try:
            db_schema = get_table_info()
            schema_text = json.dumps(db_schema, indent=2)
            schema_freshly_loaded = True

            if isinstance(db_schema, dict):
                logger.info(f"Schema freshly loaded with {len(db_schema)} tables.")

        except Exception as e:
            logger.error(f"sql_generator_node failed to get db_schema: {e}")
            return {
                "db_schema": "",
                "response": f"sql_generator_node failed to get db_schema: {e}"
            }
    else:
        schema_text = json.dumps(db_schema, indent=2) if isinstance(db_schema, dict) else str(db_schema)
        logger.info("Using cached schema from state.")

    system_prompt = PROMPTS.get("sql_generator", query=user_message, db_schema=schema_text)

    messages = [
        SystemMessage(content=system_prompt),
        *conversation_history
    ]

    response = llm.invoke(messages)
    logger.info(f"sql_generator_node response: {response}")

    new_messages = [
        HumanMessage(content=user_message),
        AIMessage(content=response.content)
    ]

    try:
        sql_query = response.content.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    except Exception as e:
        logger.error(f"sql_generator_node failed: {e}")
        sql_query = ""

    logger.info(f"[sql_generator_node] detected sql_query: {sql_query}")

    return {
        "db_schema": db_schema,
        "sql_query": sql_query,
        "response": sql_query,
        "messages": new_messages
    }