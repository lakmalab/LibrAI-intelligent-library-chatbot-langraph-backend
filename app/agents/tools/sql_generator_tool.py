import json
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool

from app.agents.llm_provider import get_llm
from app.agents.prompts.registry import PROMPTS
from app.core.logger import logger
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

    def _run(self, user_query: str, schema_info: str, messages: List = None, **kwargs) -> str:
        logger.info(f"[sql_generator_tool] called")

        conversation_history = messages or []
        user_message = user_query
        db_schema = str(schema_info)
        #logger.info(f"[sql_generator_tool] result: {db_schema}")

        system_prompt = PROMPTS.get("sql_generator").format( query=user_message, db_schema=db_schema)
        logger.info(f"[SQLGeneratorTool system_prompt] : {system_prompt}")

        messages = [
            SystemMessage(content=system_prompt),
            *conversation_history,
            HumanMessage(content=user_query)
        ]

        response = self.llm.invoke(messages)
        logger.info(f"[SQLGeneratorTool] result: {response}")
        try:
            sql_query = response.content.strip().replace('```sql', '').replace('```', '').strip()
        except Exception as e:
            logger.error(f"sql_generator_tool failed parsing SQL: {e}")
            sql_query = ""

        logger.info(f"sql_query: {sql_query}")
        return sql_query

    async def _arun(self, user_query: str, schema_info: str, messages: List = None, **kwargs) -> Dict[str, Any]:
        return self._run(user_query, schema_info, messages, **kwargs)