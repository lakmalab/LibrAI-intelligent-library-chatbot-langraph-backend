import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from app.schemas.chat import ChatMessageResponse, ChatMessageRequest, ConversationResponse, \
    ConversationListResponse, MessageHistory, ChatHistoryResponse, CredentialApprovalRequest
from app.services.chat_service import ChatService, get_chat_service
from app.services.session_service import SessionService, get_session_service

logger = logging.getLogger(__name__)


class ChatController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
        self._register_routes()

    def _register_routes(self):
        self.router.post("/message", response_model=ChatMessageResponse)(self.send_message)
        self.router.get("/conversations/{session_id}", response_model=ConversationListResponse)(self.get_user_conversations)
        self.router.get("/conversations/new/{session_id}", response_model=ConversationListResponse)(self.add_new_conversation)
        self.router.get("/history/{conversation_id}", response_model=ChatHistoryResponse)(self.get_chat_history)
        self.router.post("/approve-credential", response_model=ChatMessageResponse)(self.approve_credentials)

    async def send_message(
            self,request: ChatMessageRequest,chat_service: ChatService = Depends(get_chat_service)
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

    async def approve_credentials(
            self,
            request: CredentialApprovalRequest,
            chat_service: ChatService = Depends(get_chat_service)
    ):
        return await chat_service.approve_credentials(
            session_id=request.session_id,
            conversation_id=request.conversation_id,
            approved=request.approved,
            modified_email=request.modified_email,
            modified_password=request.modified_password
        )

    async def get_user_conversations(
            self,
            session_id: str,
            chat_service: ChatService = Depends(get_chat_service),
     ):
        return await chat_service.get_user_conversations(session_id=session_id)

    async def add_new_conversation(
            self,
            session_id: str,
            chat_service: ChatService = Depends(get_chat_service),
            session_service: SessionService = Depends(get_session_service)
    ):
        if not session_service.is_session_valid(session_id):
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        return await chat_service.add_new_conversation(session_id=session_id)


    async def get_chat_history(
            self,
            conversation_id: int,
            chat_service: ChatService = Depends(get_chat_service),
    ):

        return await chat_service.get_chat_history(conversation_id=conversation_id)

chat_controller = ChatController()
router = chat_controller.router