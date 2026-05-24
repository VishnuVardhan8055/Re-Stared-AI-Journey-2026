from typing import TypedDict

class EmailState(TypedDict, total=False):
    user_request: str
    to_email: str
    subject: str
    body: str
    result: dict