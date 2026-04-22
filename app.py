import json
import re

# Load Knowledge Base
with open("knowledge_base.json", "r") as file:
    data = json.load(file)

# Memory
memory = []

# Lead State
lead = {
    "active": False,
    "step": 0,
    "name": "",
    "email": "",
    "platform": "",
    "plan": ""
}

# Lead Capture Function
def mock_lead_capture(name, email, platform, plan):
    print("\nLead Captured Successfully")
    print("Name:", name)
    print("Email:", email)
    print("Platform:", platform)
    print("Selected Plan:", plan)

# Show Pricing
def show_pricing():
    print("\nBasic Plan")
    print(data["basic_plan"]["price"])
    print(data["basic_plan"]["videos"])
    print(data["basic_plan"]["resolution"])

    print("\nPro Plan")
    print(data["pro_plan"]["price"])
    print(data["pro_plan"]["videos"])
    print(data["pro_plan"]["resolution"])
    print(data["pro_plan"]["feature"])

# Email Validation
def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

print("AutoStream AI Bot Started")
print("Type exit to stop\n")

while True:
    msg = input("You: ")
    low = msg.lower()
    memory.append(msg)

    # Exit
    if low == "exit":
        print("Bot: Thank you!")
        break

    # Lead Collection Process
    if lead["active"]:

        if lead["step"] == 1:
            lead["name"] = msg
            lead["step"] = 2
            print("Bot: Enter your email:")
            continue

        elif lead["step"] == 2:
            if valid_email(msg):
                lead["email"] = msg
                lead["step"] = 3
                print("Bot: Enter your platform:")
            else:
                print("Bot: Invalid email. Enter again:")
            continue

        elif lead["step"] == 3:
            lead["platform"] = msg

            mock_lead_capture(
                lead["name"],
                lead["email"],
                lead["platform"],
                lead["plan"]
            )

            # Reset
            lead = {
                "active": False,
                "step": 0,
                "name": "",
                "email": "",
                "platform": "",
                "plan": ""
            }
            continue

    # Greeting
    if "hi" in low or "hello" in low or "hey" in low:
        print("Bot: Hello! Welcome to AutoStream.")

    # High Intent
    elif ("buy" in low or
          "signup" in low or
          "interested" in low or
          "basic plan" in low or
          "pro plan" in low or
          "want basic" in low or
          "want pro" in low):

        if "basic" in low:
            lead["plan"] = "Basic Plan"
        elif "pro" in low:
            lead["plan"] = "Pro Plan"
        else:
            lead["plan"] = "Not Selected"

        print("Bot: Great! Please enter your name:")
        lead["active"] = True
        lead["step"] = 1

    # Pricing
    elif ("price" in low or
          "pricing" in low or
          "cost" in low or
          "plan" in low or
          "plans" in low):
        show_pricing()

    # Policy
    elif "refund" in low:
        print("Bot:", data["policy"]["refund"])

    elif "support" in low:
        print("Bot:", data["policy"]["support"])

    # Memory
    elif "memory" in low:
        print("Bot Last Messages:", memory[-5:])

    # Default
    else:
        print("Bot: Ask pricing, plans, refund or signup.")