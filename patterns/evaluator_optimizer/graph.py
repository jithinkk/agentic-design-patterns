from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from patterns.evaluator_optimizer.nodes import evaluate, generate, route_after_evaluate


class EvaluatorState(TypedDict, total=False):
    task: str
    criteria: str
    solution: str
    feedback: str
    passed: bool
    iteration: int
    max_iterations: int


def build_graph():
    builder = StateGraph(EvaluatorState)

    builder.add_node("generate", generate)
    builder.add_node("evaluate", evaluate)

    builder.add_edge(START, "generate")
    builder.add_edge("generate", "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {"accept": END, "give_up": END, "revise": "generate"},
    )

    return builder.compile()
