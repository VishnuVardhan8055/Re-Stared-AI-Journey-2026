# agents/reviewer_agent.py
from llm.ollama_client import get_model
import json, re

model = get_model()

PROMPT = """You are a professional email reviewer.
Review and improve the email draft below to make it polite, complete, and professional.

Return ONLY a valid JSON object:
{
  "subject": "...",
  "body": "..."
}

Rules:
- Keep to_email unchanged (do not include it in output)
- Improve subject if needed
- Make body complete, warm, and professional
- Return ONLY the JSON, no extra text
"""

def reviewer_agent_node(state):
    subject = state.get("subject", "").strip()
    body = state.get("body", "").strip()
    to_email = state.get("to_email", "").strip()

    draft = f"Subject: {subject}\nBody: {body}"
    response = model.invoke(f"{PROMPT}\n\nEmail draft:\n{draft}")
    text = response.content.strip()

    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        parsed = json.loads(text)
        return {
            "subject": parsed.get("subject", subject).strip(),
            "body": parsed.get("body", body).strip()
        }
    except Exception:
        # Keep original if review fails
        return {"subject": subject, "body": body}