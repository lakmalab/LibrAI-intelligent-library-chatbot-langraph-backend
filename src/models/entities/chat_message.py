from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.dbconnection import Base
from src.enums.role import RoleType


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(SQLEnum(RoleType, name="role_type"), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.role}>"