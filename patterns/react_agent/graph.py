from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from patterns.react_agent.nodes import call_model
from shared.tools.basic import ALL_TOOLS


def build_graph():
    builder = StateGraph(MessagesState)

    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
    builder.add_edge("tools", "agent")

    # LangGraph has no compile-time recursion cap -- it's set per invoke()
    # call instead (see run.py's DEFAULT_RECURSION_LIMIT); calling
    # build_graph().invoke(...) directly, bypassing run.py, is still
    # unbounded. No checkpointer either -- nothing persists across a crash.
    # See docs/harnesses-and-loops.md ("Guardrails", "Memory").
    return builder.compile()
