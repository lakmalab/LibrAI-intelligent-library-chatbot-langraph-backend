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
                "message": "I need 1000 pension",
                "session_id": "user_123",
                "conversation_id": 1,
            }
        }



class ChatMessageResponse(BaseModel):
    conversation_id: int
    response: str
    intent: Optional[str] = None
    metadata: dict = Field(default_factory=dict)



