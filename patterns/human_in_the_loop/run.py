from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402

from patterns.human_in_the_loop.graph import build_graph  # noqa: E402
from shared.render import block, header, step, truncate  # noqa: E402

DEFAULT_TASK = "Send a message to Alice: the report is ready."

# LangGraph's own default if unset -- made explicit and overridable rather
# than implicit, per ai-harnesses's docs/harnesses-and-loops.md ("Guardrails")
# -- https://github.com/jithinkk/ai-harnesses/blob/main/docs/harnesses-and-loops.md.
# Verified
# empirically (not assumed): recursion_limit applies fresh to each separate
# invoke() call on a thread_id, so the pre-interrupt run and the post-resume
# run are budgeted independently, not cumulatively -- a human taking a long
# time to approve doesn't eat into either budget.
DEFAULT_RECURSION_LIMIT = 25


def main(
    task: str = DEFAULT_TASK,
    approve: bool = True,
    thread_id: str = "demo",
    recursion_limit: int = DEFAULT_RECURSION_LIMIT,
) -> dict:
    """Runs the graph to completion, auto-resolving any approval pause.

    A real UI would show `pending` to a human and call `app.invoke(Command(resume=...), config)`
    only after they respond; this scripts both halves for a non-interactive demo/CLI.
    """
    app = build_graph()
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": recursion_limit}

    result = app.invoke({"messages": [HumanMessage(content=task)]}, config)
    pending_interrupts = result.get("__interrupt__")

    if not pending_interrupts:
        return {"interrupted": False, "result": result}

    resumed = app.invoke(Command(resume=approve), config)
    return {"interrupted": True, "pending": pending_interrupts[0].value, "approved": approve, "result": resumed}


def render(outcome: dict) -> str:
    """Narrate `react_agent`'s loop plus the approval gate: a side-effecting
    tool call pauses the graph (`interrupt()`) until a human decides, and
    resume is a *separate* `invoke()` call carrying that decision."""
    lines = [header("human-in-the-loop", "react loop + an approval gate before any side-effecting tool")]

    if not outcome["interrupted"]:
        lines.append(step("no gated tool was called → ran straight through, exactly like react_agent"))
    else:
        pending = outcome["pending"]
        calls = pending.get("tool_calls", []) if isinstance(pending, dict) else []
        for tc in calls:
            args = ", ".join(f"{k}={v!r}" for k, v in tc.get("args", {}).items())
            lines.append(step(f"agent → tool call: {tc.get('name')}({args})"))
        verdict = "APPROVED" if outcome["approved"] else "DENIED"
        lines.append(step(f"gate  → needs approval → PAUSED (interrupt())"))
        lines.append(step(f"        human decision: {verdict}   [delivered by a second invoke(Command(resume=…))]"))
        if not outcome["approved"]:
            lines.append(step("        tool skipped; a denial ToolMessage goes back to the agent"))

    for msg in outcome["result"]["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            continue
        if isinstance(msg, ToolMessage):
            lines.append(step(f"tools → observation: {truncate(msg.content, 60)}"))
        elif isinstance(msg, AIMessage) and msg.content:
            lines.append(step(f"agent → answer: {truncate(msg.content, 60)}"))

    lines.append(block("final messages", "\n".join(
        f"[{m.__class__.__name__.replace('Message', '')}] {m.content}"
        for m in outcome["result"]["messages"]
        if m.content  # the tool-call AIMessage has empty content; the trace above already showed it
    )))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    print(render(main(task)))
