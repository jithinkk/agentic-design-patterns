"""Node functions for the human-in-the-loop pattern.

Extends `react_agent`'s tool loop with an approval gate: before any tool
call that does something real (here, `send_message`) actually runs, the
graph pauses via LangGraph's `interrupt()` and waits for a human decision.
Read-only tool calls (calculator, search_docs, word_count) skip the gate
entirely and run immediately, same as in `react_agent`.
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt

from shared.llm.factory import get_chat_model
from shared.tools.basic import HITL_TOOLS

SYSTEM_PROMPT = (
    "You are a helpful assistant. Use a tool when it would help; sending a "
    "message is a real action with consequences, so only do it when asked."
)

TOOLS_REQUIRING_APPROVAL = {"send_message"}

_SEND_MESSAGE_RE = re.compile(r"send (?:a )?message to (\w+)[:,]?\s+(.+)", re.IGNORECASE)


def _last_human_content(messages: list[BaseMessage]) -> str:
    return next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    last = messages[-1]
    if isinstance(last, ToolMessage):
        if "denied" in last.content.lower():
            return AIMessage(content="Understood — I won't do that.")
        return AIMessage(content=f"Done: {last.content}")

    question = _last_human_content(messages)

    send_match = _SEND_MESSAGE_RE.search(question)
    if send_match:
        recipient, body = send_match.group(1), send_match.group(2)
        return AIMessage(
            content="",
            tool_calls=[{"name": "send_message", "args": {"recipient": recipient, "body": body}, "id": "call_1"}],
        )

    expr_match = re.search(r"[-+*/().\d\s]{3,}", question)
    if expr_match and any(op in expr_match.group() for op in "+-*/") and any(c.isdigit() for c in expr_match.group()):
        return AIMessage(
            content="",
            tool_calls=[{"name": "calculator", "args": {"expression": expr_match.group().strip()}, "id": "call_1"}],
        )

    return AIMessage(content=f"[fake-llm] No side-effecting action needed for: {question}")


_llm = get_chat_model(responder=_fake_responder)
_llm_with_tools = _llm.bind_tools(HITL_TOOLS)


def call_model(state: dict) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = _llm_with_tools.invoke(messages)
    return {"messages": [response]}


def route_after_agent(state: dict) -> str:
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", None)
    if not tool_calls:
        return "end"
    if any(tc["name"] in TOOLS_REQUIRING_APPROVAL for tc in tool_calls):
        return "needs_approval"
    return "tools"


def request_approval(state: dict) -> dict:
    """Pauses the graph and waits for a human decision.

    Re-runs from the top on resume (LangGraph's documented interrupt
    behavior), so everything before `interrupt()` here must be safe to
    repeat — it only reads state, never mutates anything external.
    """
    last = state["messages"][-1]
    pending = [tc for tc in last.tool_calls if tc["name"] in TOOLS_REQUIRING_APPROVAL]

    decision = interrupt(
        {
            "action": "approve_tool_calls",
            "tool_calls": [{"name": tc["name"], "args": tc["args"]} for tc in pending],
        }
    )

    if decision:
        return {"approved": True}

    denial_messages = [
        ToolMessage(content="Denied by human reviewer.", tool_call_id=tc["id"], name=tc["name"]) for tc in pending
    ]
    return {"approved": False, "messages": denial_messages}


def route_after_approval(state: dict) -> str:
    return "tools" if state["approved"] else "agent"
