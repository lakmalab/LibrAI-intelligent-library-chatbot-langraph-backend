from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")
    session_id: str = Field(..., description="Unique session identifier")
    conversation_id: Optional[int] = Field(None, description="Conversation ID if continuing existing conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "is harry potter book available",
                "session_id": "cd1db89b-5b4b-4613-863a-c8d932b1ca05",
                "conversation_id": 5,
            }
        }



class ChatMessageResponse(BaseModel):
    conversation_id: int
    response: str
    intent: Optional[str] = None
    metadata: dict = Field(default_factory=dict)



