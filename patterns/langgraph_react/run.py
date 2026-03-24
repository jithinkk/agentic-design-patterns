from dotenv import load_dotenv
load_dotenv()

from graph import build_graph


if __name__ == "__main__":
    app = build_graph()

    while True:
        user_input = input("\nAsk: ")

        if user_input.lower() == "exit":
            break

        result = app.invoke({
            "messages": [
                {"role": "user", "content": user_input}
            ]
        })

        print("\nResponse:\n")
        print(result["messages"][-1]["content"])