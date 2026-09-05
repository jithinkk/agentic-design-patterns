from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402

from patterns.human_in_the_loop.graph import build_graph  # noqa: E402

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


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    outcome = main(task)

    if not outcome["interrupted"]:
        print("No approval needed for this request.\n")
    else:
        print(f"Paused for approval: {outcome['pending']}")
        print(f"Auto-{'approved' if outcome['approved'] else 'denied'} for this demo run.\n")

    for message in outcome["result"]["messages"]:
        role = message.__class__.__name__.replace("Message", "")
        print(f"[{role}] {message.content}")
