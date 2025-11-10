from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.agents.nodes.intent_router_node import intent_router_node
from app.agents.nodes.sql_generator_node import sql_generator_node
from app.agents.state import AgentState
from app.core.logger import get_logger
from app.enums.intent import intents
from app.enums.routes import routes

logger = get_logger("build_graph")
def build_graph():
    workflow = StateGraph(AgentState)

    def route_after_intent(state: AgentState) -> str:
        intent = state.get("intent")
        logger.info(f"Intent: {intent}")

        if intent == intents.SQL_QUERY:
            return intents.SQL_QUERY
        if intent == intents.RAG_QUERY:
            return intents.RAG_QUERY
        return intents.GENERAL

    workflow.add_node(routes.INTENT_ROUTER_NODE, intent_router_node)
    workflow.add_node(routes.SQL_GENERATOR_NODE, sql_generator_node)

    workflow.set_entry_point(routes.INTENT_ROUTER_NODE)

    workflow.add_conditional_edges(
        routes.INTENT_ROUTER_NODE,
        route_after_intent,
        {
            intents.SQL_QUERY: routes.SQL_GENERATOR_NODE,
            intents.RAG_QUERY: END,
            intents.GENERAL: END
        }
    )
    workflow.add_edge(routes.SQL_GENERATOR_NODE, END)

    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)