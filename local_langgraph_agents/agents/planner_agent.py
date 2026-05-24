from llm.ollama_client import get_llm
from prompts.planner_prompt import PLANNER_PROMPT

llm = get_llm()

def planner_node(state):
    user_input = state["input"]

    response = llm.invoke([
        ("system", PLANNER_PROMPT),
        ("human", f"User request: {user_input}")
    ])

    return {"plan": response.content}