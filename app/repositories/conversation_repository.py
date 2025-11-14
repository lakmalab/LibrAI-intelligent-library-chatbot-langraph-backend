from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation_by_session_id(self, session_id: str) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .first()
        )

    def get_or_create_conversation(
            self,
            session_id: str,
            conversation_id: Optional[int] = None,
            title: str = "New Conversation"
    ) -> Conversation:

        if conversation_id is not None:
            convo = (
                self.db.query(Conversation)
                .filter(
                    Conversation.id == conversation_id,
                    Conversation.session_id == session_id
                )
                .first()
            )
            if convo:
                return convo

        latest = (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.updated_at.desc())
            .first()
        )

        if latest:
            return latest

        new_conversation = Conversation(
            session_id=session_id,
            title=title
        )

        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)

        return new_conversation

    def create_conversation(self, conversation_data: dict) -> Conversation:
        new_conversation = Conversation(**conversation_data)
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        return new_conversation

    def get_conversations_by_session_id(self, session_id: str) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def update_conversation_title(self, conversation_id: int, title: str) -> Optional[Conversation]:
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.title = title
            self.db.commit()
            self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: int) -> bool:
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False