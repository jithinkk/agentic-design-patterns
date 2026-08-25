import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from patterns.react_agent import nodes
from patterns.react_agent.graph import build_graph
from patterns.react_agent.run import main
from shared.llm.factory import get_chat_model
from shared.tools.basic import ALL_TOOLS


def test_calls_the_calculator_tool_and_answers():
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content="What is (12 + 8) * 3?")]})

    messages = result["messages"]
    assert any(
        isinstance(m, AIMessage) and m.tool_calls and m.tool_calls[0]["name"] == "calculator"
        for m in messages
    )
    assert any(isinstance(m, ToolMessage) and m.content == "60" for m in messages)
    assert "60" in messages[-1].content


def test_calls_search_docs_for_a_glossary_question():
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content="Explain what langgraph is used for")]})

    messages = result["messages"]
    assert any(
        isinstance(m, AIMessage) and m.tool_calls and m.tool_calls[0]["name"] == "search_docs"
        for m in messages
    )
    assert "LangGraph" in messages[-1].content


def test_answers_directly_when_no_tool_is_needed():
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content="What is the capital of France?")]})

    messages = result["messages"]
    assert not any(isinstance(m, ToolMessage) for m in messages)
    assert "No tool needed" in messages[-1].content


def test_recursion_limit_stops_a_runaway_tool_calling_loop(monkeypatch):
    """Regression test: proves the cap actually stops something, not just
    that the config key is set. A model that never stops calling a tool
    would otherwise loop until this hits some other resource limit."""

    def always_call_calculator(messages):
        return AIMessage(
            content="",
            tool_calls=[{"name": "calculator", "args": {"expression": "1+1"}, "id": "call_x"}],
        )

    monkeypatch.setattr(
        nodes, "_llm_with_tools", get_chat_model(responder=always_call_calculator).bind_tools(ALL_TOOLS)
    )

    with pytest.raises(GraphRecursionError):
        main("This will never stop calling a tool", recursion_limit=6)
