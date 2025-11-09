import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate

from src.agents import prompt_templates
from src.agents.llm_provider import get_llm
from src.agents.state import AgentState
from src.enums.ai_model import AiModel

logger = logging.getLogger(__name__)
def intent_router_node(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, model=AiModel.GPT_5_NANO)

    conversation_history = state.get("messages", [])
    user_message = state.get("user_query", "")

    prompt_template = PromptTemplate(
        template=prompt_templates.INTENT_ROUTER_TEMPLATE,
        input_variables=["query"]
    )

    formatted_system_prompt = prompt_template.format(query=user_message)

    messages = [
        SystemMessage(content=formatted_system_prompt),
        *conversation_history,
        HumanMessage(content='Return output ONLY as valid JSON in this format: {"intent": "intent_name"}')
    ]

    response = llm.invoke(messages)
    logger.info("Intent classification response:", response)

    try:
        result = json.loads(response.content)
        intent = result.get("intent", "other").strip().lower()
    except Exception as e:
        logger.error("Intent classification failed:", e)
        intent = "other"

    state["intent"] = intent
    logger.info(f"[IntentClassifier] detected intent: {intent}")
    return state