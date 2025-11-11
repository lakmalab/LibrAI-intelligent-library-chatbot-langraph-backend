from enum import Enum

class routes(str, Enum):
    INTENT_ROUTER_NODE = "intent_router_node"
    SQL_GENERATOR_NODE = "sql_generator_node"
    EXECUTE_SQL_TOOL_NODE = "execute_sql_tool_node"
    GENERATE_CONVERSATIONAL_RESPONSE_NODE = "generate_conversational_response_node"
