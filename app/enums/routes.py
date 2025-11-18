from enum import Enum

class routes(str, Enum):
    INTENT_ROUTER_NODE = "intent_router_node"
    GENERATE_CONVERSATIONAL_RESPONSE_NODE = "generate_conversational_response_node"
    GET_TABLE_INFO_NODE = "get_table_info_node"
    HUMAN_REVIEW_NODE = "credential_review_node"
    GENERATE_SQL_QUERY_NODE = "generate_sql_query_node"
    EXECUTE_SQL_QUERY_NODE = "execute_sql_query_node"