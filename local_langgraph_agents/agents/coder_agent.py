from llm.ollama_client import get_llm
from prompts.coder_prompt import CODER_PROMPT

llm = get_llm()

def coder_node(state):
    user_input = state["input"]
    plan = state["plan"]

    response = llm.invoke([
        ("system", CODER_PROMPT),
        ("human", f"User request: {user_input}\n\nImplementation plan:\n{plan}")
    ])

    return {"code": response.content}