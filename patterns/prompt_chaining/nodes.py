"""Node functions for the prompt-chaining pattern.

Three LLM calls run in a fixed sequence, each consuming the previous step's
output, with a plain Python "gate" between the first two steps that can
halt the chain before spending more tokens on a bad outline.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from shared.llm.factory import get_chat_model

MIN_SECTIONS = 2


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    system = messages[0].content if messages else ""
    user = messages[-1].content if messages else ""

    if "STAGE: OUTLINE" in system:
        return AIMessage(
            content=f"1. Introduction to {user}\n2. Core idea\n3. Worked example\n4. Takeaways"
        )
    if "STAGE: EXPAND" in system:
        sections = [line.strip() for line in user.splitlines() if line.strip()]
        paragraphs = "\n\n".join(
            f"## {line.split('.', 1)[-1].strip()}\nDraft paragraph covering: {line}." for line in sections
        )
        return AIMessage(content=paragraphs)
    if "STAGE: POLISH" in system:
        return AIMessage(content=user.strip() + "\n\n(tightened for clarity and flow)")
    return AIMessage(content="")


_llm = get_chat_model(responder=_fake_responder)


def generate_outline(state: dict) -> dict:
    messages = [
        SystemMessage(
            content="STAGE: OUTLINE. Produce a numbered outline (one section per line) for the given topic."
        ),
        HumanMessage(content=state["topic"]),
    ]
    response = _llm.invoke(messages)
    return {"outline": response.content}


def gate_check(state: dict) -> dict:
    """Programmatic checkpoint between LLM calls: no model call here at all."""
    sections = [line for line in state["outline"].splitlines() if line.strip()]
    passed = len(sections) >= MIN_SECTIONS
    reason = (
        f"outline has {len(sections)} section(s), need at least {MIN_SECTIONS} to continue"
        if not passed
        else f"outline has {len(sections)} sections, proceeding"
    )
    return {"gate_passed": passed, "gate_reason": reason}


def route_after_gate(state: dict) -> str:
    return "continue" if state["gate_passed"] else "stop"


def expand_draft(state: dict) -> dict:
    messages = [
        SystemMessage(content="STAGE: EXPAND. Expand this outline into a short draft, one paragraph per section."),
        HumanMessage(content=state["outline"]),
    ]
    response = _llm.invoke(messages)
    return {"draft": response.content}


def polish(state: dict) -> dict:
    messages = [
        SystemMessage(content="STAGE: POLISH. Tighten and polish this draft without changing its meaning."),
        HumanMessage(content=state["draft"]),
    ]
    response = _llm.invoke(messages)
    return {"final": response.content}
