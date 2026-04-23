# AutoStream AI Sales Agent

A conversational AI agent built for **AutoStream** — a fictional SaaS platform for automated video editing. The agent qualifies leads from social media conversations using intent detection, RAG-powered knowledge retrieval, and structured tool execution.

Built as part of the **ServiceHive / Inflx** Machine Learning Intern assignment.

---

## Features

| Capability | Implementation |
|---|---|
| Intent Classification | LLM-based classifier (greeting / product_inquiry / high_intent / unknown) |
| RAG Knowledge Retrieval | TF-IDF retriever over a local Markdown knowledge base |
| Lead Collection | Stateful multi-turn form (name → email → platform) |
| Tool Execution | `mock_lead_capture()` called only after all 3 fields are collected |
| Memory | Full conversation history retained via LangGraph `AgentState` |
| LLM Provider | Groq (free) — `llama-3.1-8b-instant` by default |

---

## Project Structure

```
autostream-agent/
├── agent/
│   ├── graph.py          # LangGraph graph definition (nodes + edges)
│   ├── intent.py         # LLM-based intent classifier
│   └── state.py          # AgentState TypedDict
├── knowledge_base/
│   └── autostream_kb.md  # Pricing, features, and policies
├── rag/
│   └── retriever.py      # TF-IDF retriever over the knowledge base
├── tools/
│   └── lead_capture.py   # mock_lead_capture() tool
├── main.py               # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/autostream-agent.git
cd autostream-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
# Edit .env and add your API key
```

The default provider is **Groq** (free at [console.groq.com](https://console.groq.com)). It uses `llama-3.1-8b-instant` by default — you can switch to `llama-3.3-70b-versatile` or `mixtral-8x7b-32768` via the `GROQ_MODEL` env var. Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` to use those providers instead.

### 5. Run the agent

```bash
python main.py
```

### Example conversation

```
You: Hi, tell me about your pricing.
Agent: AutoStream offers two plans...

You: That sounds great. I want to try the Pro plan for my YouTube channel.
Agent: Great choice! Could you share your full name?

You: Alex Johnson
Agent: Thanks, Alex! What's the best email address to reach you at?

You: alex@example.com
Agent: Almost there! Which creator platform do you primarily use?

You: YouTube
Agent: You're all set, Alex! 🎉 We've captured your details...
```

---

## Architecture Explanation

### Why LangGraph?

LangGraph was chosen over a simple chain or AutoGen because this agent requires **explicit, inspectable state transitions** across multiple conversation turns. The lead collection flow is inherently a multi-step form — the agent must remember which fields it has already collected, validate inputs (e.g., email format), and only trigger the tool once all three values are present. LangGraph's `StateGraph` makes these transitions first-class citizens: each node reads from and writes to a shared `AgentState`, and conditional edges encode the routing logic cleanly. This avoids the fragility of prompt-only memory management and makes the flow easy to extend (e.g., adding a "company size" field later requires only a new edge condition).

### State Management

`AgentState` is a `TypedDict` with five fields:

- `messages` — full conversation history, accumulated via LangGraph's `add_messages` reducer
- `intent` — the classified intent of the latest user turn
- `lead_info` — a dict tracking collected `name`, `email`, and `platform`
- `awaiting_field` — which field the agent is currently waiting for (`"name"`, `"email"`, `"platform"`, or `None`)
- `lead_captured` — boolean flag set to `True` after `mock_lead_capture()` is called

The graph is invoked once per user turn. Between turns, the full state dict is persisted in memory by the calling loop in `main.py`, giving the agent memory across 5–6+ conversation turns without any external database.

### RAG Pipeline

The knowledge base (`autostream_kb.md`) is split into semantic chunks on Markdown headers. At query time, a TF-IDF vectorizer scores each chunk against the user's message and returns the top-3 most relevant chunks. These are injected into the system prompt of the RAG node, grounding the LLM's answer in factual product data.

---

## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, the recommended approach uses the **WhatsApp Business Cloud API** (Meta) with a webhook-based architecture:

### Architecture

```
WhatsApp User
     │  (sends message)
     ▼
Meta WhatsApp Cloud API
     │  (HTTP POST to your webhook)
     ▼
FastAPI / Flask Webhook Server   ←── hosted on AWS / GCP / Railway
     │
     ├── Verify webhook token (GET /webhook)
     └── Handle incoming message (POST /webhook)
              │
              ▼
        Session Store (Redis / DynamoDB)
              │  (load AgentState by phone number)
              ▼
        LangGraph Agent (graph.invoke(state))
              │
              ▼
        Updated AgentState  ──► Save back to session store
              │
              ▼
        Meta Send Message API  ──► Reply to user on WhatsApp
```

### Key Steps

1. **Register a webhook** on the Meta Developer Portal pointing to `https://yourdomain.com/webhook`.
2. **Verify the webhook** by responding to Meta's `GET` challenge with the hub token.
3. **On each `POST`**, extract `from` (phone number) and `text.body` from the payload.
4. **Load the session** for that phone number from Redis (keyed by phone number).
5. **Run `graph.invoke(state)`** with the new `HumanMessage` appended.
6. **Save the updated state** back to Redis with a TTL (e.g., 30 minutes of inactivity).
7. **Send the AI reply** back via a `POST` to `https://graph.facebook.com/v19.0/{phone_id}/messages`.

This approach is stateless at the server level (state lives in Redis), making it horizontally scalable. Each WhatsApp conversation maps to one LangGraph state object, preserving full memory across turns exactly as in the CLI version.

---

## Evaluation Checklist

- [x] Intent detection (greeting / product_inquiry / high_intent / unknown)
- [x] RAG over local knowledge base (pricing, features, policies)
- [x] Multi-turn lead collection with field validation
- [x] `mock_lead_capture()` called only after all 3 fields are collected
- [x] Full conversation memory via LangGraph `AgentState`
- [x] Clean modular code structure
- [x] WhatsApp deployment explanation
