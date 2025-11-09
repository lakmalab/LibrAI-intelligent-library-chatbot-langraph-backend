import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_core._pydantic_core import ValidationError
from fastapi import APIRouter, Depends, Request
from src.schemas.chat import ChatMessageResponse, ChatMessageRequest
from src.schemas.session import SessionResponse
from src.services.chat_service import ChatService, get_chat_service
from src.services.session_service import SessionService, get_session_service

logger = logging.getLogger(__name__)


class SessionController:
    def __init__(self):
        self.router = APIRouter(prefix="/v1/session", tags=["Session"])
        self._register_routes()

    def _register_routes(self):
        self.router.post("/create", response_model=SessionResponse)(self.create_session)

    async def create_session(
            self,request: Request,
            session_service: SessionService = Depends(get_session_service)
    ):
        try:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

            new_session = session_service.create_session(ip_address, user_agent)
            return new_session

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create_session: {str(e)}"
            )

SessionController = SessionController()
router = SessionController.router