"""Node functions for the ReAct (Reason + Act) tool-using agent pattern.

A single `agent` node repeatedly calls the model; the model either emits a
tool call (routed to LangGraph's prebuilt `ToolNode`, whose result loops
back to `agent`) or a plain answer (which ends the run). This is the loop
underneath most "autonomous agent" frameworks.
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from shared.llm.factory import get_chat_model
from shared.tools.basic import ALL_TOOLS

SYSTEM_PROMPT = (
    "You are a helpful assistant. Use a tool when it would help answer the "
    "question; otherwise answer directly from what you know."
)

_DOC_TERMS = ("langgraph", "react", "orchestrator", "evaluator")


def _last_human_content(messages: list[BaseMessage]) -> str:
    return next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    last = messages[-1]
    if isinstance(last, ToolMessage):
        return AIMessage(content=f"The answer is {last.content}.")

    question = _last_human_content(messages)
    lowered = question.lower()

    expr_match = re.search(r"[-+*/().\d\s]{3,}", question)
    if expr_match and any(op in expr_match.group() for op in "+-*/") and any(c.isdigit() for c in expr_match.group()):
        return AIMessage(
            content="",
            tool_calls=[{"name": "calculator", "args": {"expression": expr_match.group().strip()}, "id": "call_1"}],
        )

    if any(term in lowered for term in _DOC_TERMS):
        return AIMessage(
            content="",
            tool_calls=[{"name": "search_docs", "args": {"query": question}, "id": "call_1"}],
        )

    if "word count" in lowered or "how many words" in lowered:
        return AIMessage(
            content="",
            tool_calls=[{"name": "word_count", "args": {"text": question}, "id": "call_1"}],
        )

    return AIMessage(content=f"[fake-llm] No tool needed here: {question}")


_llm = get_chat_model(responder=_fake_responder)
_llm_with_tools = _llm.bind_tools(ALL_TOOLS)


def call_model(state: dict) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = _llm_with_tools.invoke(messages)
    return {"messages": [response]}
