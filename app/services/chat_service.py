from typing import Dict, Any

from fastapi import Depends

from app.agents import prompt_templates
from app.agents.graph import build_graph
from app.db.dbconnection import get_db, get_table_info
from app.enums import RoleType
from app.models import ChatMessage
from app.models.session import Session
from app.repositories.chat_repository import ChatRepository
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatMessageResponse
from app.core.logger import get_logger

logger = get_logger("chat_service")

class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.conversation_repo = ConversationRepository(db)
        self.agent = build_graph()

    async def process_chat_message(self, request) -> ChatMessageResponse:
        try:
            conversation = self.conversation_repo.get_conversation_by_session_id(request.session_id)
            if conversation is None:
                conversation = self.conversation_repo.create_conversation({
                    "session_id": request.session_id,
                    "title": "New Conversation"
                })
        except Exception as e:
            logger.error(e)
            raise e

        thread_config = {
            "configurable": {
                "thread_id": f"{request.session_id}_conv_{conversation.id}"
            }
        }

        agent_state = {
            "user_query": request.message,
            "session_id": request.session_id,
            "conversation_id": conversation.id,
        }

        result = await self.agent.ainvoke(agent_state, config=thread_config)

        #logger.info(f"Final message : {result}")

        response_text = result.get("response", "I'm sorry, I couldn't process that.")
        intent = result.get("intent")

        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.USER,
            content=request.message
        )
        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.ASSISTANT,
            content=response_text,
            intent=intent
        )

        return ChatMessageResponse(
            conversation_id=conversation.id,
            response=response_text,
            intent=intent,
            metadata={"request": request.model_dump()}
        )

    def save_message(
            self,
            conversation_id: int,
            role: RoleType,
            content: str,
            intent: str = None,
            metadata: Dict[str, Any] = None
    ) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            metadata=metadata
        )
        self.chat_repo.save_message(message)

        return message

_chat_service_instance = None

def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(db)
    return _chat_service_instance