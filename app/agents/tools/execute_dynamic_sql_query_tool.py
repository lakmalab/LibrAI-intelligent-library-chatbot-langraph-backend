from langchain_core.tools import BaseTool
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from typing import Dict, Any, Coroutine
import json

from app.core.logger import get_logger
from app.db.dbconnection import get_db

_db_session: DBSession = None


def set_db_session(db: DBSession):
    global _db_session
    _db_session = db

logger = get_logger("sql_generator_tool")
class QueryExecutorTool(BaseTool):
    name: str = "query_executor"
    description: str = "Executes SQL queries and returns results in JSON format"

    def _run(self, sql_query: str, **kwargs) -> Dict[str, Any]:
        """
        Run a SQL query and return the results in a simple format.

        Args:
            sql_query: The SQL query string to execute

        Returns:
            JSON string containing query results or error information
        """
        logger.info(f"[QueryExecutorTool] called")
        try:
            if _db_session:
                db_session = _db_session
            else:
                db_session = next(get_db())

            result = db_session.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

            data = [dict(zip(columns, row)) for row in rows]
            logger.info(f"[QueryExecutorTool] {data}")
            return {
                "success": True,
                "row_count": len(data),
                "data": data,
                "query": sql_query
            }

        except Exception as e:
            return  {
                "success": False,
                "error": str(e),
                "query": sql_query
            }
