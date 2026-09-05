import asyncio

import pytest

# `mcp` ships in the optional `mcp` group. Skipping keeps `pytest`
# green for a contributor who ran a plain `uv sync`; CI installs the group.
pytest.importorskip("mcp")

from shared.tools.mcp_server import mcp  # noqa: E402

EXPECTED_TOOLS = {"calculate", "search_documentation", "count_words", "send_a_message"}


def _call(name: str, arguments: dict) -> str:
    """Invoke a tool in-process and return its text content.

    No transport, no subprocess, no sockets: `MCPServer.call_tool` is
    directly awaitable, which is what makes the server unit-testable under
    the repo's "runs offline with no API key" guarantee.
    """
    result = asyncio.run(mcp.call_tool(name, arguments))
    assert result.is_error is False, result.content
    return result.content[0].text


def test_exposes_exactly_the_four_repo_tools():
    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == EXPECTED_TOOLS
    # Every tool needs a description; harnesses show these to the model and
    # an unlabelled tool is effectively unusable.
    assert all(t.description for t in tools)


def test_schemas_are_generated_from_type_hints():
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}

    calc = tools["calculate"].input_schema
    assert calc["properties"]["expression"]["type"] == "string"
    assert calc["required"] == ["expression"]

    # The one two-argument tool, to prove multi-arg schemas survive the wrap.
    send = tools["send_a_message"].input_schema
    assert set(send["required"]) == {"recipient", "body"}


def test_calculate_evaluates_and_reaches_the_real_tool():
    assert _call("calculate", {"expression": "(12 + 8) * 3"}) == "60"


def test_calculate_keeps_the_underlying_guardrails():
    """The DoS bound lives in shared/tools/basic.py; wrapping must not lose it.

    A regression here would mean the MCP surface is a way around the
    protection rather than a view onto the same tool.
    """
    out = _call("calculate", {"expression": "99999999**99999999"})
    assert "error" in out.lower()


def test_search_documentation_and_count_words():
    assert "LangGraph" in _call("search_documentation", {"query": "langgraph"})
    assert _call("count_words", {"text": "one two three"}) == "3"


def test_send_a_message_is_exposed_as_a_callable_tool():
    """Effectful, and deliberately not gated here.

    `patterns/human_in_the_loop` gates this call inside the graph. Over MCP
    the gate belongs to the harness, which is exactly the contrast the
    server's docstring draws -- so the tool itself must simply work.
    """
    assert "Message sent to Alice" in _call(
        "send_a_message", {"recipient": "Alice", "body": "the report is ready"}
    )
