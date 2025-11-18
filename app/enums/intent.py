from enum import Enum

class intents(str, Enum):
    SQL_QUERY = "sql_query"
    RAG_QUERY = "rag_query"
    GENERAL = "general_chat"
    HITL = "human_in_the_loop"
    REJECTED = "reject_sql"