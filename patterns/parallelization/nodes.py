"""Node functions for the parallelization ("sectioning") pattern.

Three independent LLM calls each analyze the same input text along a
different dimension. Because none of them depend on each other's output,
LangGraph runs them in the same superstep instead of one after another,
and a plain aggregation step joins the results once all three land.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from shared.llm.factory import get_chat_model

_POSITIVE_WORDS = ("great", "good", "love", "excellent", "happy", "amazing")
_NEGATIVE_WORDS = ("bad", "terrible", "hate", "awful", "angry", "poor")
_STOPWORDS = {
    "the", "a", "an", "is", "was", "of", "to", "and", "in", "it", "this",
    "that", "for", "on", "with", "as", "at", "by", "from", "but", "are",
}


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    system = messages[0].content if messages else ""
    user = messages[-1].content if messages else ""

    if "STAGE: SENTIMENT" in system:
        lowered = user.lower()
        if any(w in lowered for w in _NEGATIVE_WORDS):
            return AIMessage(content="negative")
        if any(w in lowered for w in _POSITIVE_WORDS):
            return AIMessage(content="positive")
        return AIMessage(content="neutral")

    if "STAGE: SUMMARY" in system:
        first_sentence = user.split(".")[0].strip()
        return AIMessage(content=f"{first_sentence}." if first_sentence else user[:80])

    if "STAGE: KEYWORDS" in system:
        words = [w.strip(".,!?").lower() for w in user.split()]
        candidates = [w for w in words if w and w not in _STOPWORDS and len(w) > 3]
        seen: list[str] = []
        for w in candidates:
            if w not in seen:
                seen.append(w)
        return AIMessage(content=", ".join(seen[:5]))

    return AIMessage(content="")


_llm = get_chat_model(responder=_fake_responder)


def analyze_sentiment(state: dict) -> dict:
    messages = [
        SystemMessage(content="STAGE: SENTIMENT. Reply with one word: positive, negative, or neutral."),
        HumanMessage(content=state["text"]),
    ]
    return {"sentiment": _llm.invoke(messages).content}


def summarize(state: dict) -> dict:
    messages = [
        SystemMessage(content="STAGE: SUMMARY. Summarize this text in one sentence."),
        HumanMessage(content=state["text"]),
    ]
    return {"summary": _llm.invoke(messages).content}


def extract_keywords(state: dict) -> dict:
    messages = [
        SystemMessage(content="STAGE: KEYWORDS. List up to 5 comma-separated keywords for this text."),
        HumanMessage(content=state["text"]),
    ]
    return {"keywords": _llm.invoke(messages).content}


def aggregate(state: dict) -> dict:
    """Pure Python join — aggregation doesn't have to be another LLM call."""
    report = (
        "## Analysis Report\n\n"
        f"**Sentiment:** {state['sentiment']}\n\n"
        f"**Summary:** {state['summary']}\n\n"
        f"**Keywords:** {state['keywords']}\n"
    )
    return {"report": report}
