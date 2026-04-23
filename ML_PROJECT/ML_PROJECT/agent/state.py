"""
LangGraph state definition for the AutoStream conversational agent.
All fields are carried across every node in the graph.
"""

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class LeadInfo(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]


class AgentState(TypedDict):
    # Full conversation history (LangGraph managed list)
    messages: Annotated[list, add_messages]

    # Detected intent for the latest user turn
    # Values: "greeting" | "product_inquiry" | "high_intent" | "unknown"
    intent: str

    # Tracks which lead fields have been collected
    lead_info: LeadInfo

    # True once mock_lead_capture has been called successfully
    lead_captured: bool

    # Which field the agent is currently waiting for from the user
    # Values: "name" | "email" | "platform" | None
    awaiting_field: Optional[str]
