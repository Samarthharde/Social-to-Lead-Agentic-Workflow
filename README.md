# 🚀 AutoStream AI Agent

> Social-to-Lead Conversational AI Agent for AutoStream SaaS Platform

---

# 📌 Project Overview

AutoStream is a fictional SaaS company that provides automated video editing tools for content creators.

This project is an AI-powered conversational agent that converts conversations into qualified business leads.

The bot can:

- Understand user intent
- Answer pricing and product questions
- Detect high-intent users
- Collect lead details
- Trigger lead capture workflow
- Maintain conversation memory

---

# 🎯 Features

## 1. Intent Detection

The chatbot identifies:

- Greeting Intent
- Product / Pricing Inquiry
- High-Intent Signup Lead

---

## 2. RAG Knowledge Retrieval

Uses a local JSON knowledge base to answer questions dynamically.

### Basic Plan
- $29/month
- 10 videos/month
- 720p resolution

### Pro Plan
- $79/month
- Unlimited videos
- 4K resolution
- AI captions

### Policies
- No refunds after 7 days
- 24/7 support only for Pro plan

---

## 3. Lead Capture Workflow

When user shows buying intent, bot asks:

- Name
- Email
- Creator Platform

After collecting all values:

Lead Captured Successfully

---

## 4. Memory / State Management

The bot stores:

- Previous user messages
- Current signup step
- User lead details

---

# 🛠️ Tech Stack

- Python 3.9+
- JSON
- Rule-Based NLP Logic

---

# 📁 Project Structure

AutoStream_Project/
app.py
knowledge_base.json
requirements.txt
README.md
demo_script.txt

---

# ▶️ How to Run Project

## Step 1

Install Python 3.9+

## Step 2

Open terminal inside project folder

## Step 3

Run:

python app.py

---

# 💬 Example Chat

You: hi  
Bot: Hello! Welcome to AutoStream.

You: pricing  
Bot: Shows Basic and Pro Plans

You: I want pro plan  
Bot: Please enter your name

You: Samarth  
Bot: Enter your email

You: sam@gmail.com  
Bot: Enter your platform

You: YouTube

Lead Captured Successfully

---

# 🧠 Architecture Explanation

This project uses Python as the backend logic layer.

User messages are processed through rule-based intent detection using keyword matching. Based on the identified intent, the chatbot determines whether the user needs pricing details, support information, or signup assistance.

A local JSON file acts as the knowledge base and provides dynamic answers for pricing, features, and policy-related questions. This simulates a lightweight Retrieval-Augmented Generation (RAG) workflow.

State management is handled using Python dictionaries and lists. The bot tracks whether the user is currently in the lead signup flow, remembers collected details, and stores recent messages for conversation continuity.

Once Name, Email, and Platform are collected, the lead capture tool is triggered successfully.

---

# 📱 WhatsApp Deployment (Webhook Integration)

This chatbot can be deployed on WhatsApp using Flask + Twilio API.

## Workflow

1. Create Flask webhook endpoint
2. Connect Twilio WhatsApp Sandbox
3. Receive incoming messages
4. Send messages to chatbot logic
5. Return chatbot reply to WhatsApp user

This enables real-time AI conversations directly on WhatsApp.


---

# ✅ Assignment Requirements Covered

- Intent Detection
- Knowledge Retrieval
- State Management
- Tool Calling Logic
- Multi-turn Memory
- Real-world Deployment Ready

---

# 👨‍💻 Author

Samarth Harde