# graph/workflow.py
from langgraph.graph import StateGraph, END
from graph.state import EmailState
from agents.email_agent import email_agent_node
from agents.reviewer_agent import reviewer_agent_node
from tools.email_tool import send_email_node

def route_after_extract(state):
    if not state.get("to_email"):
        return "end"
    return "review"

def build_graph():
    builder = StateGraph(EmailState)

    builder.add_node("extract_email", email_agent_node)
    builder.add_node("review_email", reviewer_agent_node)
    builder.add_node("send_email", send_email_node)

    builder.set_entry_point("extract_email")

    builder.add_conditional_edges(
        "extract_email",
        route_after_extract,
        {
            "review": "review_email",
            "end": END
        }
    )

    builder.add_edge("review_email", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()