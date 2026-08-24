from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from patterns.react_agent.graph import build_graph


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
