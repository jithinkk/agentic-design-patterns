from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402

from patterns.react_agent.graph import build_graph  # noqa: E402

DEFAULT_QUESTION = "What is (12 + 8) * 3?"

# LangGraph's own default if unset -- made explicit and overridable rather
# than implicit, per ai-harnesses's docs/harnesses-and-loops.md ("Guardrails")
# -- https://github.com/jithinkk/ai-harnesses/blob/main/docs/harnesses-and-loops.md.
# A runaway
# tool-calling loop hits this and raises GraphRecursionError instead of
# spinning forever.
DEFAULT_RECURSION_LIMIT = 25


def main(question: str = DEFAULT_QUESTION, recursion_limit: int = DEFAULT_RECURSION_LIMIT) -> dict:
    app = build_graph()
    return app.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"recursion_limit": recursion_limit},
    )


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
    result = main(question)

    for message in result["messages"]:
        role = message.__class__.__name__.replace("Message", "")
        tool_calls = getattr(message, "tool_calls", None)
        suffix = f" tool_calls={tool_calls}" if tool_calls else ""
        print(f"[{role}] {message.content}{suffix}")
