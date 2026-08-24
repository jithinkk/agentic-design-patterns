"""Node functions for the orchestrator-workers pattern.

Unlike `parallelization`, the number and shape of the parallel subtasks
isn't known ahead of time — the orchestrator LLM decides it at runtime.
That's what `langgraph.types.Send` is for: the routing function after
`orchestrator` returns one `Send("worker", ...)` per subtask, LangGraph
runs them all in parallel, and their results accumulate into
`worker_results` via the `operator.add` reducer before `synthesizer` runs.
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.types import Send

from shared.llm.factory import get_chat_model

_DEFAULT_TOPICS = ["an overview", "key considerations"]


def _extract_topics(task: str) -> list[str]:
    lowered = task.lower()
    marker = "covering"
    if marker not in lowered:
        return list(_DEFAULT_TOPICS)

    tail = task[lowered.index(marker) + len(marker) :].strip().rstrip(".")
    parts = re.split(r",| and ", tail)
    topics = [p.strip() for p in parts if p.strip()]
    return topics or list(_DEFAULT_TOPICS)


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    system = messages[0].content if messages else ""
    user = messages[-1].content if messages else ""

    if "STAGE: ORCHESTRATE" in system:
        topics = _extract_topics(user)
        return AIMessage(content="\n".join(f"- {topic}" for topic in topics))

    if "STAGE: WORKER" in system:
        return AIMessage(content=f"Findings on {user}: three relevant points worth including in the report.")

    if "STAGE: SYNTHESIZE" in system:
        return AIMessage(content="# Final Report\n\n" + user)

    return AIMessage(content="")


_llm = get_chat_model(responder=_fake_responder)


def orchestrator(state: dict) -> dict:
    messages = [
        SystemMessage(
            content="STAGE: ORCHESTRATE. Break this task into a short bullet list of independent subtasks, one per line."
        ),
        HumanMessage(content=state["task"]),
    ]
    response = _llm.invoke(messages)
    subtasks = [line.lstrip("-* ").strip() for line in response.content.splitlines() if line.strip()]
    return {"subtasks": subtasks}


def continue_to_workers(state: dict) -> list[Send]:
    """Conditional-edge routing function: fans out to one `worker` run per subtask."""
    return [Send("worker", {"subtask": subtask}) for subtask in state["subtasks"]]


def worker(state: dict) -> dict:
    """Runs once per subtask via `Send`; `state` here is just `{"subtask": ...}`."""
    subtask = state["subtask"]
    messages = [
        SystemMessage(content="STAGE: WORKER. Research and write findings for this specific subtask."),
        HumanMessage(content=subtask),
    ]
    response = _llm.invoke(messages)
    return {"worker_results": [{"subtask": subtask, "result": response.content}]}


def synthesizer(state: dict) -> dict:
    sections = "\n\n".join(f"### {r['subtask']}\n{r['result']}" for r in state["worker_results"])
    messages = [
        SystemMessage(content="STAGE: SYNTHESIZE. Weave these section findings into one cohesive report."),
        HumanMessage(content=sections),
    ]
    response = _llm.invoke(messages)
    return {"final_report": response.content}
