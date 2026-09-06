from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402

from patterns.react_agent.graph import build_graph  # noqa: E402
from shared.render import block, header, step, truncate  # noqa: E402

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


def render(result: dict) -> str:
    """Narrate the tool-call loop turn by turn: each `agent` turn either
    emits a tool call (observed, then back to `agent`) or a final answer
    (the loop ends). This is the shape under most "autonomous agent" SDKs."""
    messages = result["messages"]
    lines = [header("react-agent", "reason → act → observe loop; the model decides each turn")]

    turn = 0
    tool_calls = 0
    for msg in messages:
        if isinstance(msg, AIMessage):
            turn += 1
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls += 1
                    args = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                    lines.append(step(f"turn {turn}  agent → tool call: {tc['name']}({args})"))
            else:
                lines.append(step(f"turn {turn}  agent → answer (no tool call) — loop ends"))
        elif isinstance(msg, ToolMessage):
            lines.append(step(f"        tools → observation: {truncate(msg.content, 60)}"))

    answer = messages[-1].content if messages else ""
    lines.append(block("answer", answer))
    lines.append(step(f"{tool_calls} tool call(s) over {turn} agent turn(s)", indent=0))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
    print(render(main(question)))
