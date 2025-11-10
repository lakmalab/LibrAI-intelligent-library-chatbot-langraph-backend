import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from src.schemas.chat import ChatMessageResponse, ChatMessageRequest
from src.services.chat_service import ChatService, get_chat_service

logger = logging.getLogger(__name__)


class ChatController:
    def __init__(self):
        self.router = APIRouter(prefix="/v1/chat", tags=["Chat"])
        self._register_routes()

    def _register_routes(self):
        self.router.post("/message", response_model=ChatMessageResponse)(self.send_message)

    async def send_message(
            self,request: ChatMessageRequest,
            chat_service: ChatService = Depends(get_chat_service)
    ) -> ChatMessageResponse:

        try:
            result = await chat_service.process_chat_message(request)
            logger.info(
                f"Successfully processed message for session: {request.session_id}, "
                f"conversation: {result.conversation_id}"
            )

            return result

        except ValidationError as e:
            error_msg = f"Invalid request data: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        except Exception as e:
            error_msg = f"Failed to process message: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )


chat_controller = ChatController()
router = chat_controller.router