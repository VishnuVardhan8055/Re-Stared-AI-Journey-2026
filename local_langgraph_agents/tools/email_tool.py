# import os
# import smtplib
# from email.mime.text import MIMEText
#
# def send_email_tool(to_email: str, subject: str, body: str):
#     sender_email = "polankivishnuvardhan27@gmail.com"
#     #app_password = os.getenv("GMAIL_APP_PASSWORD")
#     app_password = "mtkx niiv pjsi uskc"
#
#     if not app_password:
#         return {"status": "error", "message": "Missing GMAIL_APP_PASSWORD"}
#
#     msg = MIMEText(body)
#     msg["Subject"] = subject
#     msg["From"] = sender_email
#     msg["To"] = to_email
#
#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(sender_email, app_password)
#             server.sendmail(sender_email, [to_email], msg.as_string())
#         return {"status": "success", "message": f"Email sent to {to_email}"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}
#


import os
import smtplib
from email.mime.text import MIMEText

def send_email_tool(to_email: str, subject: str, body: str):
    sender_email = "vishnuaids2020to2024@gmail.com"
    app_password = "mtkx niiv pjsi uskc"

    if not app_password:
        return {"status": "error", "message": "Missing GMAIL_APP_PASSWORD"}

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, [to_email], msg.as_string())
        return {"status": "success", "message": f"Email sent to {to_email}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_email_node(state):
    to_email = state.get("to_email", "").strip()
    subject = state.get("subject", "").strip()
    body = state.get("body", "").strip()

    if not to_email:
        return {"result": {"status": "error", "message": "Missing recipient email"}}

    if not subject:
        subject = "No Subject"

    if not body:
        body = "Hello"

    result = send_email_tool(to_email, subject, body)
    return {"result": result}