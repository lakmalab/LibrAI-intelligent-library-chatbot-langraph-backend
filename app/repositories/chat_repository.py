from app.models import ChatMessage
from app.models.session import Session


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


