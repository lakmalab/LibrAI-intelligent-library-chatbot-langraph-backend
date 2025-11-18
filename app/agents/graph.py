from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.agents.nodes.conversation_node import generate_conversational_response
from app.agents.nodes.credential_review_node import credential_review_node
from app.agents.nodes.execute_sql_query_node import execute_sql_query_node
from app.agents.nodes.generate_sql_query_node import generate_sql_query_node
from app.agents.nodes.get_db_info_node import get_table_info_node

from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query_tool import QueryExecutorTool
from app.core.logger import get_logger
from app.enums.intent import intents
from app.enums.routes import routes
from app.enums.tool_call import toolcall

logger = get_logger("build_graph")
def build_graph():
    workflow = StateGraph(AgentState)


    def route_after_get_db_info(state: AgentState) -> str:
        if state.get("can_answer_from_db") and state.get("need_to_interrupt"):
            logger.info("ROUTING TO HITL")
            return intents.HITL
        elif state.get("can_answer_from_db") and not state.get("need_to_interrupt"):
            logger.info("ROUTING TO GENERATE_SQL_QUERY_NODE")
            return intents.SQL_QUERY
        else:
            logger.info("ROUTING TO GENERATE_CONVERSATIONAL_RESPONSE_NODE")
            return intents.GENERAL

    def route_after_credential_review(state: AgentState) -> str:
        if state.get("credentials_approved", False) and state.get("credentials_reviewed", False):
            logger.info("Credentials approved, proceeding to next step")
            return routes.GENERATE_SQL_QUERY_NODE
        else:
            logger.info("Credentials not approved, returning to conversation")
            return routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE

    workflow.add_node(routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE, generate_conversational_response)
    workflow.add_node(routes.GET_TABLE_INFO_NODE, get_table_info_node)
    workflow.add_node(routes.HUMAN_REVIEW_NODE, credential_review_node)
    workflow.add_node(routes.GENERATE_SQL_QUERY_NODE, generate_sql_query_node)
    workflow.add_node(routes.EXECUTE_SQL_QUERY_NODE, execute_sql_query_node)

    workflow.set_entry_point(routes.GET_TABLE_INFO_NODE)

    workflow.add_conditional_edges(
        routes.GET_TABLE_INFO_NODE,
        route_after_get_db_info,
        {
            intents.SQL_QUERY: routes.GENERATE_SQL_QUERY_NODE,
            intents.HITL: routes.HUMAN_REVIEW_NODE,
            intents.GENERAL: routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE
        }
    )

    workflow.add_edge(routes.GENERATE_SQL_QUERY_NODE, routes.EXECUTE_SQL_QUERY_NODE)
    workflow.add_edge(routes.EXECUTE_SQL_QUERY_NODE, routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE)

    workflow.add_conditional_edges(
        routes.HUMAN_REVIEW_NODE,
        route_after_credential_review,
        {
            routes.GENERATE_SQL_QUERY_NODE: routes.GENERATE_SQL_QUERY_NODE,
            routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE: routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE
        }
    )

    workflow.add_edge(routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE, END)

    memory = InMemorySaver()
    compiled_graph = workflow.compile(
        checkpointer=memory,
        interrupt_after=[routes.HUMAN_REVIEW_NODE]
    )

    # try:
    #     try:
    #         mermaid_text = compiled_graph.get_graph().draw_mermaid()
    #         logger.info("Graph structure (Mermaid):")
    #         logger.info(mermaid_text)
    #
    #         with open("agent_workflow_graph.mmd", "w") as f:
    #             f.write(mermaid_text)
    #         logger.info("Graph saved as 'agent_workflow_graph.mmd'")
    #     except Exception as e:
    #         logger.debug(f"Mermaid text generation failed: {e}")
    #
    #     try:
    #         image_bytes = compiled_graph.get_graph().draw_mermaid_png()
    #         with open("agent_workflow_graph.png", "wb") as f:
    #             f.write(image_bytes)
    #         logger.info("Graph saved as 'agent_workflow_graph.png'")
    #     except Exception as e:
    #         logger.debug(f"PNG generation failed: {e}")
    #
    # except Exception as e:
    #     logger.info(f"Graph visualization skipped: {e}")
    #     logger.info("Graph is functional, visualization is optional")

    return compiled_graph