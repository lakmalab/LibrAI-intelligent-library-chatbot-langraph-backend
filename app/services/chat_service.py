from typing import Dict, Any

from fastapi import Depends

from app.agents.graph import build_graph
from app.db.dbconnection import get_db
from app.enums import RoleType
from app.enums.intent import intents
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

        if result.get("awaiting_human_approval", False):
            logger.info("SQL query requires human approval")

            pending_review = result.get("pending_review", {})

            response_text = pending_review.get("summary") or pending_review.get(
                "message") or "Please review the SQL query."

            return ChatMessageResponse(
                conversation_id=conversation.id,
                response=response_text,
                intent=result.get("intent"),
                metadata={
                    "request": request.model_dump(),
                    "requires_approval": True,
                    "sql_query": pending_review.get("generated_sql_query")
                },
                session_id=request.session_id,
                approved=False
            )

        pending_review = result.get("pending_review", {})
        response_text = pending_review.get("summary") or pending_review.get("message") or "Please review the SQL query."

        return ChatMessageResponse(
            conversation_id=conversation.id,
            response=result.get("response", "I'm sorry, I couldn't process that."),
            intent=result.get("intent"),
            metadata={
                "request": request.model_dump(),
                "requires_approval": result.get("awaiting_human_approval", False),
                "sql_query": pending_review.get("generated_sql_query")
            },
            session_id=request.session_id,
            approved=True
        )

    async def approve_sql_query(self, session_id: str, conversation_id: int, approved: bool,
                                modified_query: str = None) -> ChatMessageResponse:

        thread_config = {
            "configurable": {
                "thread_id": f"{session_id}_conv_{conversation_id}"
            }
        }

        current_state = await self.agent.aget_state(thread_config)

        if not approved:
            logger.info("SQL query rejected by human")

            await self.agent.aupdate_state(
                thread_config,
                {
                    "sql_approved": False,
                    "sql_reviewed": True,
                    "awaiting_human_approval": False,
                    "rejection_reason": "User rejected the query"
                }
            )
            update_values = {
                "sql_approved": False,
                "sql_reviewed": True,
                "awaiting_human_approval": False
            }
            if modified_query:
                update_values["intent"] = intents.REJECTED
                logger.info("Using modified SQL query from human")

            await self.agent.aupdate_state(
                thread_config,
                {
                    "sql_approved": False,
                    "sql_reviewed": True,
                    "awaiting_human_approval": False,
                    "rejection_reason": "User rejected the query",
                    "intent": "rejected"
                },
                as_node="human_review_node"
            )

            result = await self.agent.ainvoke(None, config=thread_config)

            response_text = result.get("response", "Query was rejected. How else can I help you?")

            return ChatMessageResponse(
                conversation_id=conversation_id,
                response=str(response_text),
                intent=result.get("intent"),
                metadata={
                    "approved": False,
                    "rejected": True
                },
                session_id=session_id,
                approved=False
            )

        else:
            logger.info("SQL query approved by human")

            update_values = {
                "sql_approved": True,
                "sql_reviewed": True,
                "awaiting_human_approval": False
            }

            if modified_query:
                update_values["sql_query"] = modified_query
                logger.info("Using modified SQL query from human")

            await self.agent.aupdate_state(thread_config, update_values)

            result = await self.agent.ainvoke(None, config=thread_config)

            response_text = result.get("response", "Query processed.")
            intent = result.get("intent")

            return ChatMessageResponse(
                conversation_id=conversation_id,
                response=str(response_text),
                intent=intent,
                metadata={
                    "approved": True,
                    "modified_query": modified_query
                },
                session_id=session_id,
                approved=True
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

    async def get_user_conversations(self, session_id):
        try:
            conversations = self.conversation_repo.get_conversations_by_session_id(session_id)
            if conversations is None:
                conversations = self.conversation_repo.create_conversation({
                    "session_id": session_id,
                    "title": "New Conversation"
                })

        except Exception as e:
            logger.error(e)
            raise e

        conversations_object = {
            "session_id": session_id,
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at
                }
                for conv in conversations
            ]
        }

        return conversations_object


_chat_service_instance = None


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(db)
    return _chat_service_instance