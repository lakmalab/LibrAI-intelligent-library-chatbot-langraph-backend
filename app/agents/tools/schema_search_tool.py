from langchain_core.tools import BaseTool
from sqlalchemy import inspect
from typing import Any, Dict, List

from app.db.dbconnection import get_db

class SchemaSearchTool(BaseTool):
    name: str = "schema_search"
    description: str = ("Searches the MySQL schema using SQLAlchemy Inspector. "
                        "Returns tables and columns relevant to the natural language query. "
                        "Does NOT return full schema — only best matches.")


    def _run(self, query: str, **kwargs) -> Dict[str, Any]:
        db = next(get_db())
        inspector = inspect(db.bind)

        try:
            tables = inspector.get_table_names()

            query_lower = query.lower()

            candidates: List[Dict[str, Any]] = []

            for table in tables:
                columns = inspector.get_columns(table)
                col_names = [col["name"] for col in columns]

                score = 0
                if table.lower() in query_lower:
                    score += 2

                for col in col_names:
                    if col.lower() in query_lower:
                        score += 1

                if score > 0:
                    candidates.append({
                        "table": table,
                        "columns": col_names,
                        "score": score
                    })

            candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

            return {
                "success": True,
                "matches": candidates[:3]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
