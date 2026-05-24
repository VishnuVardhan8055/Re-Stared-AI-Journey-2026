# app.py
from graph.workflow import build_graph

def main():
    graph = build_graph()
    print("\n🤖 AI Email Agent is ready! (type 'exit' to quit)\n")

    while True:
        user_request = input("Enter your request: ").strip()

        if user_request.lower() == "exit":
            print("Goodbye! Exiting agent.")
            break

        if not user_request:
            print("Please enter a valid request.\n")
            continue

        result = graph.invoke({"user_request": user_request})

        print("\n--- FINAL RESULT ---")
        print(f"  Status  : {result.get('result', {}).get('status', 'unknown')}")
        print(f"  To      : {result.get('to_email', '')}")
        print(f"  Subject : {result.get('subject', '')}")
        print(f"  Message : {result.get('result', {}).get('message', '')}")
        print("--------------------\n")

if __name__ == "__main__":
    main()