from pydantic import BaseModel, field_validator
from pydantic import BaseModel, Field,validator
from typing import Optional
from datetime import datetime
import re

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")
    session_id: str = Field(..., description="Unique session identifier")
    conversation_id: Optional[int] = Field(None, description="Conversation ID if continuing existing conversation")

    @field_validator('message')
    def validate_message_content(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Message cannot be empty or just whitespace')

        if re.match(r'^[\d\s\W]+$', v):
            raise ValueError('Message must contain meaningful text content')

        return v

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
    session_id: Optional[str] = None
    approved: Optional[bool] = None

class SQLApprovalRequest(BaseModel):
    session_id: str
    conversation_id: int
    approved: bool
    modified_query: str = None

