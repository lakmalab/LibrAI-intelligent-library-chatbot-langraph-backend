from enum import Enum

class intents(str, Enum):
    CREDENTIALS_CHECK = "credentials_check"
    SQL_QUERY = "sql_query"
    RAG_QUERY = "rag_query"
    GENERAL = "general_chat"
    HITL = "human_in_the_loop"
    REJECTED = "reject_sql"