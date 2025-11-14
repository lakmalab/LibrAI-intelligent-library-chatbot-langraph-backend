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

    def get_messages_by_conversation_id(self, conversation_id):
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
