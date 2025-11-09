import logging

from fastapi import Depends

from src.agents.graph import build_graph
from src.database.dbconnection import get_db
from src.models.entities.session import Session
from src.repositories.chat_repository import ChatRepository
from src.repositories.conversation_repository import ConversationRepository
from src.utils.logger import get_logger

logger = get_logger("chat_service")
class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.conversation_repo = ConversationRepository(db)
        self.agent = build_graph()

    async def process_chat_message(self, request):
        try:
            conversation = self.conversation_repo.get_conversation_by_session_id(request.session_id)
            if conversation is None:
                conversation = self.conversation_repo.create_conversation({
                    "session_id": request.session_id,
                    "title": "New Conversation"
                })
        except Exception as e:
            logger.error(e)

        thread_config = {
            "configurable": {
                "thread_id": f"{request.session_id}_conv_{conversation.id}"
            }
        }
        agent_state = {
            "user_query": request.message,
            "session_id": request.session_id,
            "conversation_id": conversation.id,
            "messages": [],
        }

        result = await self.agent.ainvoke(agent_state, config=thread_config)
        response_text = result.get("response", "I'm sorry, I couldn't process that.")
        intent = result.get("intent")

        return {
            "conversation_id": 1,
            "response": response_text,
            "intent": intent,
            "metadata": {
               "request": request
            }
        }


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)