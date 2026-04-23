"""
Intent classification for the AutoStream agent.
Uses the LLM to classify user messages into one of four categories.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel


INTENT_SYSTEM_PROMPT = """You are an intent classifier for AutoStream, a SaaS video editing platform.

Classify the user's latest message into EXACTLY one of these intents:

1. greeting       – Simple hello, hi, hey, or small talk with no product question.
2. product_inquiry – Asking about features, pricing, plans, policies, or how the product works.
3. high_intent    – Clearly wants to sign up, start a trial, buy a plan, or try the product.
4. unknown        – Anything else (off-topic, unclear).

Reply with ONLY the intent label, nothing else. No punctuation, no explanation.
Examples:
  User: "Hi there!" → greeting
  User: "What's included in the Pro plan?" → product_inquiry
  User: "I want to sign up for Pro for my YouTube channel" → high_intent
  User: "What's the weather today?" → unknown
"""


def classify_intent(llm: BaseChatModel, user_message: str) -> str:
    """
    Classify the intent of a single user message.

    Returns one of: "greeting", "product_inquiry", "high_intent", "unknown"
    """
    response = llm.invoke(
        [
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
    )
    raw = response.content.strip().lower()

    # Normalise – accept partial matches in case the LLM adds extra words
    if "high_intent" in raw or "high intent" in raw:
        return "high_intent"
    if "product" in raw or "inquiry" in raw:
        return "product_inquiry"
    if "greeting" in raw:
        return "greeting"
    return "unknown"
