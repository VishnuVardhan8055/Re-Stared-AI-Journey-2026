from graph.workflow import build_graph

def main():
    graph = build_graph()
    user_request = input("Enter your request: ").strip()

    result = graph.invoke({"user_request": user_request})

    print("\nFINAL RESULT:")
    print(result)

if __name__ == "__main__":
    main()