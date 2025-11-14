import json
from typing import Dict, Any

from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool

from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.core.logger import logger
from app.db.dbconnection import get_table_info
from app.enums import AiModel


class SQLGeneratorTool(BaseTool):
    name: str = "sql_generator"
    description: str = "Generates SQL queries based on natural language questions and database schema"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)
        return self._llm

    def _run(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        logger.info(f"[sql_generator_tool] called")
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
            system_prompt = PROMPTS.get("sql_generator", query=user_message, db_schema=schema_text)
            logger.info("Sending full schema to GPT for the first time.")
        else:
            system_prompt = PROMPTS.get("sql_generator", query=user_message,
                                        db_schema="(Schema already provided in context)")
            logger.info("Schema already known, sending prompt without full schema.")

        messages = [SystemMessage(content=system_prompt), *conversation_history]

        response = self.llm.invoke(messages)
        #logger.info(f"sql_generator_tool response: {response}")

        try:
            sql_query = response.content.strip().replace('```sql', '').replace('```', '').strip()
        except Exception as e:
            logger.error(f"sql_generator_tool failed parsing SQL: {e}")
            sql_query = ""

        logger.info(f"sql_query: {sql_query}")
        return {
            "db_schema": db_schema,
            "sql_query": sql_query,
            "response_text": sql_query,
            "schema_sent_once": schema_sent_once
        }

    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(state)
