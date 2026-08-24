from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from patterns.parallelization.nodes import aggregate, analyze_sentiment, extract_keywords, summarize


class ParallelState(TypedDict, total=False):
    text: str
    sentiment: str
    summary: str
    keywords: str
    report: str


def build_graph():
    builder = StateGraph(ParallelState)

    builder.add_node("sentiment", analyze_sentiment)
    builder.add_node("summary", summarize)
    builder.add_node("keywords", extract_keywords)
    builder.add_node("aggregate", aggregate)

    # Fan out: all three run in the same superstep since none depends on
    # another's output.
    builder.add_edge(START, "sentiment")
    builder.add_edge(START, "summary")
    builder.add_edge(START, "keywords")

    # Fan in: `aggregate` only runs once all three predecessors have run.
    builder.add_edge("sentiment", "aggregate")
    builder.add_edge("summary", "aggregate")
    builder.add_edge("keywords", "aggregate")

    builder.add_edge("aggregate", END)

    return builder.compile()
