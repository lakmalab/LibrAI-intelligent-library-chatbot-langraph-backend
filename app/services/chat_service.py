from typing import Dict, Any

from fastapi import Depends

from app.agents.graph import build_graph
from app.db.dbconnection import get_db
from app.enums import RoleType
from app.enums.intent import intents
from app.models import ChatMessage, Conversation
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
            conversation = (self.conversation_repo
                            .get_or_create_conversation(request.session_id, request.conversation_id))

        except Exception as e:
            logger.error(e)
            raise e

        self.save_message(
            conversation_id=conversation.id,
            role=RoleType.USER,
            content=request.message
        )

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


        if result.get("need_to_interrupt", False):
            logger.info("credentials human approval")

            pending_review = result.get("pending_review", {})
            logger.info(f"awaiting_credential_approval:{pending_review}", )
            response_text = pending_review.get("summary") or pending_review.get(
                "message") or "Please review the SQL query."

            self.save_message(
                conversation_id=conversation.id,
                role=RoleType.ASSISTANT,
                content=response_text
            )

            return ChatMessageResponse(
                conversation_id=conversation.id,
                response=response_text,
                intent=result.get("intent"),
                metadata={
                    "request": request.model_dump(),
                    "requires_approval": True,
                    "pending_email": pending_review.get("email"),
                    "pending_password": pending_review.get("password")
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

    async def add_new_conversation(self, session_id):
        try:

            conversations = self.conversation_repo.create_conversation({
                "session_id": session_id,
                "title": "New Conversation"
            })

            conversations_object = {
                "session_id": conversations.session_id,
                "conversations": [
                    {
                        "id": conversations.id,
                        "title": conversations.title,
                        "created_at": conversations.created_at,
                        "updated_at": conversations.updated_at
                    }
                ]
            }

        except Exception as e:
            logger.error(e)
            raise e

        return conversations_object

    async def get_chat_history(self, conversation_id):

        messages = self.chat_repo.get_messages_by_conversation_id(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "intent": msg.intent,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }

    async def approve_credentials(
            self,
            session_id: str,
            conversation_id: int,
            approved: bool,
            modified_email: str = None,
            modified_password: str = None
    ) -> ChatMessageResponse:

        thread_config = {
            "configurable": {
                "thread_id": f"{session_id}_conv_{conversation_id}"
            }
        }

        current_state = await self.agent.aget_state(thread_config)

        if not approved:
            logger.info("Credentials rejected by human")

            update_values = {
                "credentials_approved": False,
                "credentials_reviewed": True,
                "awaiting_credential_approval": False,
                "rejection_reason": "User rejected the credentials",
                "intent": "credentials_rejected"
            }

            await self.agent.aupdate_state(thread_config, update_values, as_node="credential_review_node")

            result = await self.agent.ainvoke(None, config=thread_config)

            response_text = result.get("response", "Credentials were rejected. Please provide correct details.")
            self.save_message(
                conversation_id=conversation_id,
                role=RoleType.ASSISTANT,
                content=response_text
            )

            return ChatMessageResponse(
                conversation_id=conversation_id,
                response=str(response_text),
                intent=result.get("intent"),
                metadata={"approved": False, "rejected": True},
                session_id=session_id,
                approved=False
            )

        logger.info("Credentials approved by human")

        update_values = {
            "credentials_approved": True,
            "credentials_reviewed": True,
            "awaiting_credential_approval": False
        }

        if modified_email:
            update_values["email"] = modified_email
        if modified_password:
            update_values["password"] = modified_password

        await self.agent.aupdate_state(thread_config, update_values)

        result = await self.agent.ainvoke(None, config=thread_config)

        response_text = result.get("response", "Credentials confirmed.")
        intent = result.get("intent")

        return ChatMessageResponse(
            conversation_id=conversation_id,
            response=str(response_text),
            intent=intent,
            metadata={
                "approved": True,
                "modified_email": modified_email,
                "modified_password": modified_password
            },
            session_id=session_id,
            approved=True
        )


_chat_service_instance = None


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(db)
    return _chat_service_instance