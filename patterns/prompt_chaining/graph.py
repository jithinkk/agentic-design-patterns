from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from patterns.prompt_chaining.nodes import (
    expand_draft,
    gate_check,
    generate_outline,
    polish,
    route_after_gate,
)


class ChainState(TypedDict, total=False):
    topic: str
    outline: str
    gate_passed: bool
    gate_reason: str
    draft: str
    final: str


def build_graph():
    builder = StateGraph(ChainState)

    builder.add_node("generate_outline", generate_outline)
    builder.add_node("gate_check", gate_check)
    builder.add_node("expand_draft", expand_draft)
    builder.add_node("polish", polish)

    builder.add_edge(START, "generate_outline")
    builder.add_edge("generate_outline", "gate_check")
    builder.add_conditional_edges(
        "gate_check",
        route_after_gate,
        {"continue": "expand_draft", "stop": END},
    )
    builder.add_edge("expand_draft", "polish")
    builder.add_edge("polish", END)

    return builder.compile()
