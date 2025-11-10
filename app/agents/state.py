from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.enums.intent import intents


class AgentState(TypedDict):

    messages: Annotated[List, add_messages]
    user_query: str

    session_id: str
    conversation_id: Optional[int]
    intent: intents

    response: str

    db_schema: str
    sql_query:str