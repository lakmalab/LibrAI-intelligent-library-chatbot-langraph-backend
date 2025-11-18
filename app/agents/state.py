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
    tool_results: str
    sql_query:str

    generated_sql_query: Optional[str]
    sql_approved: Optional[bool]
    sql_reviewed: Optional[bool]
    awaiting_human_approval: Optional[bool]
    pending_review: Optional[Dict[str, Any]]
    rejection_reason: Optional[str]

    schema_info: str