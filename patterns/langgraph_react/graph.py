from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict


class State(TypedDict):
    messages: List[Dict]


from nodes import call_model


def build_graph():
    builder = StateGraph(State)

    builder.add_node("llm", call_model)

    builder.add_edge(START, "llm")
    builder.add_edge("llm", END)

    return builder.compile()