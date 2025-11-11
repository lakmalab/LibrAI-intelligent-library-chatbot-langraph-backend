from langchain_core.tools import tool
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text

from app.db.dbconnection import get_db

_db_session: DBSession = None

def set_db_session(db: DBSession):
    global _db_session
    _db_session = db


@tool
def execute_dynamic_sql_query(sql_query: str):
    """
    Run a SQL query and return the results in a simple format.
    """
    try:
        db_session = next(get_db())

        result = db_session.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()

        data = [dict(zip(columns, row)) for row in rows]

        return {
            "success": True,
            "row_count": len(data),
            "data": data,
            "query": sql_query
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": sql_query
        }
