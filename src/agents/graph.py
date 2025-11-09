from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.agents.state import AgentState


def build_graph():
    workflow = StateGraph(AgentState)


    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)