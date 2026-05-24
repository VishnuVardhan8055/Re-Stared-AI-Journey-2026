from llm.ollama_client import get_llm
from prompts.reviewer_prompt import REVIEWER_PROMPT

llm = get_llm()

def reviewer_node(state):
    code = state["code"]

    response = llm.invoke([
        ("system", REVIEWER_PROMPT),
        ("human", f"Review this code:\n\n{code}")
    ])

    return {
        "review": response.content,
        "final_output": code,
    }