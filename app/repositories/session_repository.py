from typing import Optional
from sqlalchemy.orm import Session
from app.models.session import Session


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_session_by_ip(self, ip_address: str) -> Optional[Session]:
        return (
            self.db.query(Session)
            .filter(Session.ip_address == ip_address)
            .order_by(Session.expires_at.desc())
            .first()
        )

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        return self.db.query(Session).filter(Session.session_id == session_id).first()

    def create_session(self, session_data: dict) -> Session:
        new_session = Session(**session_data)
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def update_session(self, session: Session) -> Session:
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: str) -> bool:
        session = self.get_session_by_id(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False