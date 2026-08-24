"""Node functions for the routing pattern.

A cheap classification step decides which of several specialized prompts
(and, in a real system, potentially different models or tools) should
handle the request. This avoids forcing a single generic prompt to be
good at every kind of query.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from shared.llm.factory import get_chat_model

CATEGORIES = ("billing", "technical", "general")

_BILLING_KEYWORDS = ("invoice", "charge", "refund", "payment", "subscription", "billed")
_TECHNICAL_KEYWORDS = ("error", "bug", "crash", "not working", "exception", "broken", "fails")


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    system = messages[0].content if messages else ""
    user = messages[-1].content if messages else ""
    lowered = user.lower()

    if "STAGE: CLASSIFY" in system:
        if any(kw in lowered for kw in _BILLING_KEYWORDS):
            return AIMessage(content="billing")
        if any(kw in lowered for kw in _TECHNICAL_KEYWORDS):
            return AIMessage(content="technical")
        return AIMessage(content="general")

    if "STAGE: BILLING" in system:
        return AIMessage(content=f"[billing specialist] Looking into your billing question: {user}")
    if "STAGE: TECHNICAL" in system:
        return AIMessage(content=f"[technical specialist] Let's debug this: {user}")
    if "STAGE: GENERAL" in system:
        return AIMessage(content=f"[general support] Happy to help: {user}")

    return AIMessage(content="")


_llm = get_chat_model(responder=_fake_responder)


def classify(state: dict) -> dict:
    messages = [
        SystemMessage(
            content=(
                "STAGE: CLASSIFY. Categorize the user's support query as exactly one "
                f"of: {', '.join(CATEGORIES)}. Respond with only that single word."
            )
        ),
        HumanMessage(content=state["query"]),
    ]
    response = _llm.invoke(messages)
    category = response.content.strip().lower()
    if category not in CATEGORIES:
        category = "general"
    return {"category": category}


def route_after_classify(state: dict) -> str:
    return state["category"]


def _handle(state: dict, stage: str) -> dict:
    messages = [
        SystemMessage(content=f"STAGE: {stage}. Respond helpfully to this {stage.lower()} support query."),
        HumanMessage(content=state["query"]),
    ]
    response = _llm.invoke(messages)
    return {"response": response.content}


def billing_handler(state: dict) -> dict:
    return _handle(state, "BILLING")


def technical_handler(state: dict) -> dict:
    return _handle(state, "TECHNICAL")


def general_handler(state: dict) -> dict:
    return _handle(state, "GENERAL")
