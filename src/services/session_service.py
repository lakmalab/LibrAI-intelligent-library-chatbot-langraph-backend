import uuid
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.utils.config import settings
from src.database.dbconnection import get_db
from src.schemas.session import SessionCreate
from src.models.entities.session import Session
from src.repositories.session_repository import SessionRepository
from src.repositories.conversation_repository import ConversationRepository


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.conversation_repo = ConversationRepository(db)

    def create_session(self, ip_address: str, user_agent: str) -> Session:
        existing_session = self.session_repo.get_latest_session_by_ip(ip_address)

        if existing_session and existing_session.expires_at > datetime.utcnow():
            conversation = self.conversation_repo.get_conversation_by_session_id(
                existing_session.session_id
            )

            if not conversation:
                self.conversation_repo.create_conversation({
                    "session_id": existing_session.session_id,
                    "title": "New Conversation"
                })

            return existing_session

        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)

        session_data = {
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": expires_at
        }

        new_session = self.session_repo.create_session(session_data)

        self.conversation_repo.create_conversation({
            "session_id": new_session.session_id,
            "title": "New Conversation"
        })

        return new_session

    def get_session(self, session_id: str) -> Session:
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return session

    def is_session_valid(self, session_id: str) -> bool:
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            return False

        if session.expires_at and session.expires_at < datetime.utcnow():
            return False

        return True

    def refresh_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        session.expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        return self.session_repo.update_session(session)

    def delete_session(self, session_id: str) -> bool:
        return self.session_repo.delete_session(session_id)

    def get_session_with_conversations(self, session_id: str):
        session = self.get_session(session_id)
        conversations = self.conversation_repo.get_conversations_by_session_id(session_id)

        return {
            "session": session,
            "conversations": conversations
        }


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return SessionService(db)