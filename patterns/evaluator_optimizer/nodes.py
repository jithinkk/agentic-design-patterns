"""Node functions for the evaluator-optimizer pattern.

`generate` proposes a solution, `evaluate` grades it against explicit
criteria and returns pass/fail plus feedback, and the graph loops back to
`generate` (with that feedback folded into the prompt) until the evaluator
passes it or `max_iterations` is reached.

Not to be confused with "evals" as a production practice (a fixed
test/benchmark set run against the whole system at dev/CI time, tracked
over releases) -- this `evaluate` node runs at runtime, inside one task,
and never leaves the graph. See ai-harnesses's docs/harnesses-and-loops.md
("Evals") -- https://github.com/jithinkk/ai-harnesses/blob/main/docs/harnesses-and-loops.md
-- for
the distinction and why this repo's own pytest suite is closer to what
that term actually means.
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from shared.llm.factory import get_chat_model

DEFAULT_MAX_ITERATIONS = 3


def _extract_field(text: str, name: str) -> str:
    match = re.search(rf"{name}: (.*?)(?:\n|$)", text)
    return match.group(1).strip() if match else ""


def _parse_criteria(criteria: str) -> tuple[str | None, int | None]:
    keyword_match = re.search(r"mention ['\"]([^'\"]+)['\"]", criteria)
    words_match = re.search(r"max(?:imum)?(?: of)? (\d+) words?", criteria)
    keyword = keyword_match.group(1) if keyword_match else None
    max_words = int(words_match.group(1)) if words_match else None
    return keyword, max_words


def _fake_responder(messages: list[BaseMessage]) -> AIMessage:
    system = messages[0].content if messages else ""
    user = messages[-1].content if messages else ""

    if "STAGE: GENERATE" in system:
        criteria = _extract_field(user, "CRITERIA")
        iteration = int(_extract_field(user, "ITERATION") or "1")
        keyword, _ = _parse_criteria(criteria)

        if iteration == 1:
            # Deliberately imperfect first draft so the loop has something to fix.
            return AIMessage(content="The future of productivity, delivered fast and simple")

        words = ([keyword] if keyword else []) + ["makes", "work", "effortless"]
        return AIMessage(content=" ".join(words))

    if "STAGE: EVALUATE" in system:
        criteria = _extract_field(user, "CRITERIA")
        solution = _extract_field(user, "SOLUTION")
        keyword, max_words = _parse_criteria(criteria)

        problems = []
        if keyword and keyword.lower() not in solution.lower():
            problems.append(f"missing required keyword {keyword!r}")
        if max_words is not None and len(solution.split()) > max_words:
            problems.append(f"has {len(solution.split())} words, over the {max_words}-word limit")

        if problems:
            return AIMessage(content="FAIL: " + "; ".join(problems))
        return AIMessage(content="PASS")

    return AIMessage(content="")


_llm = get_chat_model(responder=_fake_responder)


def generate(state: dict) -> dict:
    iteration = state.get("iteration", 0) + 1
    content = f"TASK: {state['task']}\nCRITERIA: {state['criteria']}\nITERATION: {iteration}"
    if state.get("feedback"):
        content += f"\nPREVIOUS FEEDBACK: {state['feedback']}"

    messages = [
        SystemMessage(content="STAGE: GENERATE. Propose a solution to the task that satisfies the criteria."),
        HumanMessage(content=content),
    ]
    response = _llm.invoke(messages)
    return {"solution": response.content, "iteration": iteration}


def evaluate(state: dict) -> dict:
    content = f"CRITERIA: {state['criteria']}\nSOLUTION: {state['solution']}"
    messages = [
        SystemMessage(
            content="STAGE: EVALUATE. Judge the solution against the criteria; reply 'PASS' or 'FAIL: <reasons>'."
        ),
        HumanMessage(content=content),
    ]
    response = _llm.invoke(messages)
    passed = response.content.strip().upper().startswith("PASS")
    return {"passed": passed, "feedback": response.content}


def route_after_evaluate(state: dict) -> str:
    if state["passed"]:
        return "accept"
    max_iterations = state.get("max_iterations", DEFAULT_MAX_ITERATIONS)
    if state["iteration"] >= max_iterations:
        return "give_up"
    return "revise"
