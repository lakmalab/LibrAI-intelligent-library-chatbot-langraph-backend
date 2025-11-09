from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from src.models.entities.session import Session
from src.models.entities.conversation import Conversation


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

