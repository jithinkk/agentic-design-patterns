from typing import Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from patterns.human_in_the_loop.nodes import (
    call_model,
    request_approval,
    route_after_agent,
    route_after_approval,
)
from shared.tools.basic import HITL_TOOLS


class ApprovalState(MessagesState):
    approved: bool


def build_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
    """A checkpointer is required: `interrupt()` needs persisted state to
    pause on one `invoke()` call and resume on the next. Defaults to an
    in-memory saver, which is enough for a single-process demo/test; a
    real deployment would use a durable one (e.g. Postgres-backed).

    This is pause/resume plumbing for one interrupted task, not long-term
    memory -- a fresh `thread_id` per call still starts with no history.
    See ai-harnesses's docs/harnesses-and-loops.md ("Memory") --
    https://github.com/jithinkk/ai-harnesses/blob/main/docs/harnesses-and-loops.md
    -- for the distinction and
    what a real long-term-memory setup looks like on top of this same
    primitive."""
    builder = StateGraph(ApprovalState)

    builder.add_node("agent", call_model)
    builder.add_node("human_approval", request_approval)
    builder.add_node("tools", ToolNode(HITL_TOOLS))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {"end": END, "tools": "tools", "needs_approval": "human_approval"},
    )
    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {"tools": "tools", "agent": "agent"},
    )
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=checkpointer or MemorySaver())
