from llm.ollama_client import get_model
import json, re

model = get_model()

PROMPT = """You are an email drafting assistant.
Extract the recipient email, subject, and body from the user request.

Return ONLY a valid JSON object in this exact format:
{
  "to_email": "...",
  "subject": "...",
  "body": "..."
}

Rules:
- to_email must be the email address from the request
- subject must be short and professional
- body must be a complete, polite, professional email paragraph
- Return ONLY the JSON, no extra text, no explanation
"""

def email_agent_node(state):
    user_request = state.get("user_request", "").strip()
    if not user_request:
        return {"to_email": "", "subject": "", "body": ""}

    response = model.invoke(f"{PROMPT}\n\nUser request: {user_request}")
    text = response.content.strip()

    # Extract JSON block if model adds surrounding text
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        parsed = json.loads(text)
        return {
            "to_email": parsed.get("to_email", "").strip(),
            "subject": parsed.get("subject", "").strip(),
            "body": parsed.get("body", "").strip()
        }
    except Exception:
        # Fallback: try key=value line parsing
        result = {"to_email": "", "subject": "", "body": ""}
        for line in text.splitlines():
            for key in result:
                if line.lower().startswith(key):
                    _, _, val = line.partition("=")
                    result[key] = val.strip().strip('"')
        return result