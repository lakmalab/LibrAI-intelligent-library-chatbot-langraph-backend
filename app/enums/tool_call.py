from enum import Enum

class toolcall(str, Enum):
    SQL_QUERY_GENERATE = "sql_query"
    SQL_QUERY_EXECUTE = "sql_query_execute"
    RAG_RETRIEVE = "rag_query"

