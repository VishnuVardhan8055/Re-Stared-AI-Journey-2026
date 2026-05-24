# from langchain_ollama import ChatOllama
# from tools.email_tool import send_email_tool
#
# def get_model():
#     model = ChatOllama(
#         model="gemma2:2b",
#         base_url="http://localhost:11434",
#         temperature=0
#     )
#     tools = [send_email_tool]
#     return model.bind_tools(tools), tools

from langchain_ollama import ChatOllama

def get_model():
    return ChatOllama(
        model="gemma2:2b",
        base_url="http://localhost:11434",
        temperature=0
    )