import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from patterns.orchestrator_workers.nodes import continue_to_workers, orchestrator, synthesizer, worker


class WorkerResult(TypedDict):
    subtask: str
    result: str


class OrchestratorState(TypedDict, total=False):
    task: str
    subtasks: list[str]
    worker_results: Annotated[list[WorkerResult], operator.add]
    final_report: str


def build_graph():
    builder = StateGraph(OrchestratorState)

    builder.add_node("orchestrator", orchestrator)
    builder.add_node("worker", worker)
    builder.add_node("synthesizer", synthesizer)

    builder.add_edge(START, "orchestrator")
    # Dynamic fan-out: one Send("worker", ...) per subtask decided at runtime.
    builder.add_conditional_edges("orchestrator", continue_to_workers, ["worker"])
    builder.add_edge("worker", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()
