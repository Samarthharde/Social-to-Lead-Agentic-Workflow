"""
AutoStream Conversational AI Agent – Entry Point
================================================
Run with:
    python main.py

Environment variables (set in .env or export before running):
    LLM_PROVIDER   = gemini | openai | anthropic   (default: gemini)
    GEMINI_API_KEY = <your key>
    OPENAI_API_KEY = <your key>       (if using openai)
    ANTHROPIC_API_KEY = <your key>    (if using anthropic)
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent.graph import build_graph

load_dotenv()

BANNER = """
╔══════════════════════════════════════════════════════╗
║        AutoStream AI Sales Assistant  🎬             ║
║  Powered by LangGraph + RAG  |  Type 'quit' to exit  ║
╚══════════════════════════════════════════════════════╝
"""


def run():
    print(BANNER)

    graph = build_graph()

    # Persistent state across the entire conversation
    state = {
        "messages": [],
        "intent": "unknown",
        "lead_info": {},
        "lead_captured": False,
        "awaiting_field": None,
    }

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 👋")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Agent: Thanks for chatting! Have a great day. 👋")
            break

        # Append the new human message to state
        state["messages"] = state["messages"] + [HumanMessage(content=user_input)]

        # Run the graph for this turn
        state = graph.invoke(state)

        # Print the latest AI message
        ai_messages = [m for m in state["messages"] if hasattr(m, "type") and m.type == "ai"]
        if ai_messages:
            print(f"\nAgent: {ai_messages[-1].content}\n")

        # Stop the loop if lead has been captured
        if state.get("lead_captured"):
            print("─" * 54)
            print("Lead successfully captured. Session complete.")
            print("─" * 54)
            break


if __name__ == "__main__":
    run()
