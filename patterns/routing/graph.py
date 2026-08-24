from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from patterns.routing.nodes import (
    billing_handler,
    classify,
    general_handler,
    route_after_classify,
    technical_handler,
)


class RouteState(TypedDict, total=False):
    query: str
    category: str
    response: str


def build_graph():
    builder = StateGraph(RouteState)

    builder.add_node("classify", classify)
    builder.add_node("billing", billing_handler)
    builder.add_node("technical", technical_handler)
    builder.add_node("general", general_handler)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {"billing": "billing", "technical": "technical", "general": "general"},
    )
    builder.add_edge("billing", END)
    builder.add_edge("technical", END)
    builder.add_edge("general", END)

    return builder.compile()
