# from langgraph.graph import StateGraph, START, END
# from graph.state import AgentState
# from agents.email_agent import email_agent_node
# from agents.email_send_node import email_send_node
#
# def next_step(state):
#     if state.get("intent") == "email" and state.get("to_email"):
#         return "send_email"
#     return END
#
# def build_graph():
#     builder = StateGraph(AgentState)
#
#     builder.add_node("extract_email", email_agent_node)
#     builder.add_node("send_email", email_send_node)
#
#     builder.add_edge(START, "extract_email")
#     builder.add_conditional_edges("extract_email", next_step)
#     builder.add_edge("send_email", END)
#
#     return builder.compile()


from langgraph.graph import StateGraph, END
from graph.state import EmailState
from agents.email_agent import email_agent_node
from tools.email_tool import send_email_node

def route_after_extract(state):
    if not state.get("to_email"):
        return "end"
    return "send"

def build_graph():
    builder = StateGraph(EmailState)

    builder.add_node("extract_email", email_agent_node)
    builder.add_node("send_email", send_email_node)

    builder.set_entry_point("extract_email")

    builder.add_conditional_edges(
        "extract_email",
        route_after_extract,
        {
            "send": "send_email",
            "end": END
        }
    )

    builder.add_edge("send_email", END)

    return builder.compile()