from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402

from patterns.react_agent.graph import build_graph  # noqa: E402

DEFAULT_QUESTION = "What is (12 + 8) * 3?"


def main(question: str = DEFAULT_QUESTION) -> dict:
    app = build_graph()
    return app.invoke({"messages": [HumanMessage(content=question)]})


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
    result = main(question)

    for message in result["messages"]:
        role = message.__class__.__name__.replace("Message", "")
        tool_calls = getattr(message, "tool_calls", None)
        suffix = f" tool_calls={tool_calls}" if tool_calls else ""
        print(f"[{role}] {message.content}{suffix}")
