from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.agents.nodes.conversation_node import generate_conversational_response
from app.agents.nodes.intent_router_node import intent_router_node
from app.agents.nodes.tool_caller_node import ToolCallerNode
from app.agents.nodes.human_review_node import human_review_node
from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query_tool import QueryExecutorTool
from app.agents.tools.sql_generator_tool import SQLGeneratorTool
from app.core.logger import get_logger
from app.enums.intent import intents
from app.enums.routes import routes
from app.enums.tool_call import toolcall

logger = get_logger("build_graph")


def build_graph():
    workflow = StateGraph(AgentState)

    tools = [
        SQLGeneratorTool(),
        QueryExecutorTool(),
    ]

    tool_caller_node = ToolCallerNode(tools)

    def route_after_intent(state: AgentState) -> str:
        return state.get("intent")

    def route_after_tool_call(state: AgentState) -> str:
        next_tool_call = state.get("tool_call")

        if next_tool_call == toolcall.SQL_QUERY_EXECUTE:
            if not state.get("sql_reviewed", False):
                logger.info("Routing to human review node")
                return routes.HUMAN_REVIEW_NODE
            else:
                logger.info("SQL already reviewed, executing")
                return routes.TOOL_CALLER_NODE
        else:
            return routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE


    def route_after_human_review(state: AgentState) -> str:
        if state.get("sql_approved", False) and state.get("sql_reviewed", False):
            logger.info("SQL approved, proceeding to execution")
            return routes.TOOL_CALLER_NODE
        elif state.get("sql_reviewed", False) and not state.get("sql_approved", False):
            logger.info("SQL rejected, generating rejection response")
            return routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE
        else:

            logger.info("Unexpected state in human review routing")
            return routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE

    workflow.add_node(routes.INTENT_ROUTER_NODE, intent_router_node)
    workflow.add_node(routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE, generate_conversational_response)
    workflow.add_node(routes.TOOL_CALLER_NODE, tool_caller_node)
    workflow.add_node(routes.HUMAN_REVIEW_NODE, human_review_node)

    workflow.set_entry_point(routes.INTENT_ROUTER_NODE)

    workflow.add_conditional_edges(
        routes.INTENT_ROUTER_NODE,
        route_after_intent,
        {
            intents.SQL_QUERY: routes.TOOL_CALLER_NODE,
            intents.RAG_QUERY: routes.TOOL_CALLER_NODE,
            intents.GENERAL: routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE
        }
    )

    workflow.add_conditional_edges(
        routes.TOOL_CALLER_NODE,
        route_after_tool_call,
        {
            routes.TOOL_CALLER_NODE: routes.TOOL_CALLER_NODE,
            routes.HUMAN_REVIEW_NODE: routes.HUMAN_REVIEW_NODE,
            routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE: routes.GENERATE_CONVERSATIONAL_RESPONSE_NODE
        }
    )

    workflow.add_conditional_edges(
        routes.HUMAN_REVIEW_NODE,
        route_after_human_review,
        {
            routes.TOOL_CALLER_NODE: routes.TOOL_CALLER_NODE,
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