from tools.email_tool import send_email_tool

def email_send_node(state):
    to_email = state.get("to_email", "").strip()
    subject = state.get("subject", "").strip() or "Email from agent"
    body = state.get("body", "").strip() or "Hello from AI agent"

    result = send_email_tool(
        to_email=to_email,
        subject=subject,
        body=body
    )

    return {"result": result}