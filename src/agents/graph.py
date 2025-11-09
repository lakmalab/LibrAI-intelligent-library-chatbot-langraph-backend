from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.agents.nodes.intent_router_node import intent_router_node
from src.agents.state import AgentState


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_router_node", intent_router_node)

    workflow.set_entry_point("intent_router_node")
    workflow.add_edge("intent_router_node",END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)