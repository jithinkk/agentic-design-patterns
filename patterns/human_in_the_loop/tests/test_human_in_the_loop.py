from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command

from patterns.human_in_the_loop.graph import build_graph


def test_pauses_before_a_side_effecting_tool_call():
    app = build_graph()
    config = {"configurable": {"thread_id": "pause-test"}}

    result = app.invoke({"messages": [HumanMessage(content="Send a message to Alice: report is ready")]}, config)

    assert "__interrupt__" in result
    pending = result["__interrupt__"][0].value
    assert pending["action"] == "approve_tool_calls"
    assert pending["tool_calls"][0]["name"] == "send_message"
    # The tool must NOT have run yet.
    assert not any(isinstance(m, ToolMessage) for m in result["messages"])


def test_approval_lets_the_tool_call_run():
    app = build_graph()
    config = {"configurable": {"thread_id": "approve-test"}}

    app.invoke({"messages": [HumanMessage(content="Send a message to Alice: report is ready")]}, config)
    result = app.invoke(Command(resume=True), config)

    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert "Message sent to Alice" in tool_messages[0].content
    assert "Done:" in result["messages"][-1].content


def test_denial_blocks_the_tool_call():
    app = build_graph()
    config = {"configurable": {"thread_id": "deny-test"}}

    app.invoke({"messages": [HumanMessage(content="Send a message to Bob: budget approved")]}, config)
    result = app.invoke(Command(resume=False), config)

    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].content == "Denied by human reviewer."
    assert not any("Message sent to Bob" in m.content for m in result["messages"])
    assert "won't do that" in result["messages"][-1].content


def test_read_only_tools_skip_the_approval_gate():
    app = build_graph()
    config = {"configurable": {"thread_id": "no-gate-test"}}

    result = app.invoke({"messages": [HumanMessage(content="What is (12 + 8) * 3?")]}, config)

    assert "__interrupt__" not in result
    assert any(isinstance(m, ToolMessage) and m.content == "60" for m in result["messages"])
