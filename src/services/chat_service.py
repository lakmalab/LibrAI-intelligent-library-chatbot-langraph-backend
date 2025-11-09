class ChatService:

    def __init__(self):
        pass

    async def process_chat_message(self, request):

        return {
            "conversation_id": 1,
            "response": "hi there",
            "intent": "conversation",
            "metadata": {
               "request": request
            }
        }


def get_chat_service() -> ChatService:
    return ChatService()