# from llm.ollama_client import get_model
#
# model = get_model()
#
# PROMPT = """
# Extract email information from the user request.
#
# Return exactly 4 lines in this format:
# intent=email_or_other
# to_email=...
# subject=...
# body=...
#
# If the request is about sending an email, set intent=email.
# If subject is missing, keep it empty.
# If body is missing, keep it empty.
# Return only these 4 lines.
# """
#
# def email_agent_node(state):
#     user_input = state["user_input"]
#
#     response = model.invoke(f"{PROMPT}\n\nUser request: {user_input}")
#     text = response.content.strip()
#
#     result = {
#         "intent": "other",
#         "to_email": "",
#         "subject": "",
#         "body": ""
#     }
#
#     for line in text.splitlines():
#         if "=" in line:
#             key, value = line.split("=", 1)
#             key = key.strip()
#             value = value.strip()
#             if key in result:
#                 result[key] = value
#
#     return result

# agents/email_agent.py
from llm.ollama_client import get_model

model = get_model()

PROMPT = """
You are an email drafting agent.

From the user request, extract or generate:
to_email=...
subject=...
body=...

Rules:
- Return exactly 3 lines only.
- If email is missing, keep to_email empty.
- Subject must be short and professional.
- Body must be complete and professional.
"""

def email_agent_node(state):
    user_request = state.get("user_request", "").strip()

    if not user_request:
        return {
            "result": {
                "status": "error",
                "message": "Missing user_request"
            }
        }

    response = model.invoke(f"{PROMPT}\n\nUser request: {user_request}")
    text = response.content.strip()

    parsed = {
        "to_email": "",
        "subject": "",
        "body": ""
    }

    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in parsed:
                parsed[key] = value

    return parsed