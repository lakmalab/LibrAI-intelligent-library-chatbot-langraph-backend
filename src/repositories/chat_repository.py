from datetime import datetime
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.dbconnection import get_db
from src.models.entities import ChatMessage
from src.models.entities.session import Session
from src.models.entities.conversation import Conversation


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_message(self, newChatMessage : ChatMessage) -> ChatMessage:
        try:
            self.db.add(newChatMessage)
            self.db.commit()
            self.db.refresh(newChatMessage)
        except Exception as e:
            self.db.rollback()
            raise e

        return newChatMessage


