"""
LangGraph-based conversational agent for AutoStream.

Graph topology
──────────────
  START
    │
    ▼
  classify_intent_node          ← classifies latest user message
    │
    ▼
  route_intent  ─────────────────────────────────────────────────────┐
    │                                                                 │
    │ greeting / unknown                                              │ high_intent
    ▼                                                                 │
  respond_general_node          product_inquiry                       │
                                    │                                 │
                                    ▼                                 │
                              rag_respond_node                        │
                                                                      ▼
                                                          lead_collection_node
                                                                      │
                                                          (loop until all 3 fields)
                                                                      │
                                                                      ▼
                                                          capture_lead_node
                                                                      │
                                                                    END
"""

import re
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from agent.state import AgentState
from agent.intent import classify_intent
from rag.retriever import retrieve
from tools.lead_capture import mock_lead_capture


# ──────────────────────────────────────────────
# Helper: build the LLM (lazy import so the user
# can swap providers via env vars)
# ──────────────────────────────────────────────

def _get_llm():
    """Return a configured chat LLM based on environment variables."""
    import os

    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            temperature=0.3,
        )
    else:  # default: groq
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.3,
        )


# ──────────────────────────────────────────────
# Node implementations
# ──────────────────────────────────────────────

def classify_intent_node(state: AgentState) -> dict:
    """Classify the intent of the latest human message."""
    llm = _get_llm()
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    )
    intent = classify_intent(llm, last_human)
    return {"intent": intent}


def respond_general_node(state: AgentState) -> dict:
    """Handle greetings and unknown messages with a friendly reply."""
    llm = _get_llm()

    system = SystemMessage(
        content=(
            "You are a friendly sales assistant for AutoStream, an AI-powered video editing "
            "SaaS for content creators. Keep replies short, warm, and helpful. "
            "If the user seems interested in the product, gently invite them to ask about "
            "pricing or features."
        )
    )
    response = llm.invoke([system] + state["messages"])
    return {"messages": [AIMessage(content=response.content)]}


def rag_respond_node(state: AgentState) -> dict:
    """Answer product/pricing questions using RAG over the knowledge base."""
    llm = _get_llm()

    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    )
    context = retrieve(last_human, top_k=3)

    system = SystemMessage(
        content=(
            "You are a knowledgeable sales assistant for AutoStream. "
            "Answer the user's question using ONLY the context below. "
            "Be concise and accurate. If the answer is not in the context, say so honestly.\n\n"
            f"CONTEXT:\n{context}"
        )
    )
    response = llm.invoke([system] + state["messages"])
    return {"messages": [AIMessage(content=response.content)]}


def lead_collection_node(state: AgentState) -> dict:
    """
    Collect name, email, and platform from the user one field at a time.
    Extracts values from the latest message if the agent was awaiting a field.
    """
    lead_info = dict(state.get("lead_info") or {})
    awaiting = state.get("awaiting_field")

    # ── Extract the value the agent was waiting for ──────────────────────────
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    ).strip()

    if awaiting == "name" and not lead_info.get("name"):
        lead_info["name"] = last_human

    elif awaiting == "email" and not lead_info.get("email"):
        # Basic email validation
        if re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", last_human):
            lead_info["email"] = last_human
        else:
            # Ask again
            return {
                "lead_info": lead_info,
                "awaiting_field": "email",
                "messages": [
                    AIMessage(
                        content="That doesn't look like a valid email address. "
                        "Could you double-check and re-enter it?"
                    )
                ],
            }

    elif awaiting == "platform" and not lead_info.get("platform"):
        lead_info["platform"] = last_human

    # ── Determine which field to ask for next ────────────────────────────────
    if not lead_info.get("name"):
        return {
            "lead_info": lead_info,
            "awaiting_field": "name",
            "messages": [
                AIMessage(
                    content=(
                        "Great choice! I'd love to get you set up. "
                        "Could you start by sharing your full name?"
                    )
                )
            ],
        }

    if not lead_info.get("email"):
        return {
            "lead_info": lead_info,
            "awaiting_field": "email",
            "messages": [
                AIMessage(
                    content=f"Thanks, {lead_info['name']}! What's the best email address to reach you at?"
                )
            ],
        }

    if not lead_info.get("platform"):
        return {
            "lead_info": lead_info,
            "awaiting_field": "platform",
            "messages": [
                AIMessage(
                    content="Almost there! Which creator platform do you primarily use? "
                    "(e.g. YouTube, Instagram, TikTok, Facebook…)"
                )
            ],
        }

    # All three collected — move to capture
    return {
        "lead_info": lead_info,
        "awaiting_field": None,
    }


def capture_lead_node(state: AgentState) -> dict:
    """Call mock_lead_capture and confirm to the user."""
    info = state["lead_info"]
    result = mock_lead_capture(
        name=info["name"],
        email=info["email"],
        platform=info["platform"],
    )
    confirmation = (
        f"You're all set, {info['name']}! 🎉\n\n"
        f"We've captured your details (Lead ID: {result['lead_id']}) and our team will "
        f"reach out to {info['email']} shortly to get your AutoStream Pro trial started. "
        f"Looking forward to helping you create amazing content on {info['platform']}!"
    )
    return {
        "lead_captured": True,
        "messages": [AIMessage(content=confirmation)],
    }


# ──────────────────────────────────────────────
# Routing logic
# ──────────────────────────────────────────────

def route_intent(
    state: AgentState,
) -> Literal["respond_general_node", "rag_respond_node", "lead_collection_node"]:
    """Route to the correct node based on classified intent and current state."""
    # If we're mid-collection, always continue collecting
    if state.get("awaiting_field") or (
        state.get("intent") == "high_intent" and not state.get("lead_captured")
    ):
        return "lead_collection_node"

    intent = state.get("intent", "unknown")
    if intent == "product_inquiry":
        return "rag_respond_node"
    if intent == "high_intent":
        return "lead_collection_node"
    return "respond_general_node"


def route_after_collection(
    state: AgentState,
) -> Literal["capture_lead_node", END]:  # type: ignore[valid-type]
    """After lead_collection_node, either capture or wait for next user turn."""
    info = state.get("lead_info") or {}
    if info.get("name") and info.get("email") and info.get("platform"):
        return "capture_lead_node"
    return END


# ──────────────────────────────────────────────
# Graph assembly
# ──────────────────────────────────────────────

def build_graph():
    builder = StateGraph(AgentState)

    # Register nodes
    builder.add_node("classify_intent_node", classify_intent_node)
    builder.add_node("respond_general_node", respond_general_node)
    builder.add_node("rag_respond_node", rag_respond_node)
    builder.add_node("lead_collection_node", lead_collection_node)
    builder.add_node("capture_lead_node", capture_lead_node)

    # Entry point
    builder.add_edge(START, "classify_intent_node")

    # After classification, route based on intent
    builder.add_conditional_edges(
        "classify_intent_node",
        route_intent,
        {
            "respond_general_node": "respond_general_node",
            "rag_respond_node": "rag_respond_node",
            "lead_collection_node": "lead_collection_node",
        },
    )

    # General and RAG responses end the turn
    builder.add_edge("respond_general_node", END)
    builder.add_edge("rag_respond_node", END)

    # Lead collection either captures or ends the turn (waits for next input)
    builder.add_conditional_edges(
        "lead_collection_node",
        route_after_collection,
        {
            "capture_lead_node": "capture_lead_node",
            END: END,
        },
    )

    builder.add_edge("capture_lead_node", END)

    return builder.compile()
