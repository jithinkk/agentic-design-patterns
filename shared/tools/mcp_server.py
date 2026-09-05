"""Exposes this repo's tools over MCP, so any MCP-speaking harness can call them.

[`ai-harnesses`'s Harnesses and Loops](https://github.com/jithinkk/ai-harnesses/blob/main/docs/harnesses-and-loops.md)
describes MCP as the standard way a harness integrates tools at scale, but
until now the repo only *documented* it. This closes that gap with the
smallest honest artifact: the four tools in `shared/tools/basic.py`, served
over stdio.

**Why the tools and not the patterns.** MCP exists to give an agent
*capabilities* — query this database, send this message. The seven patterns
are *architectural shapes*, not capabilities; exposing `routing` as a tool
would hand a coding agent a toy graph that sorts a fake support ticket,
which helps nobody. Tools are the part of this repo that genuinely is a
capability, so tools are the part that belongs behind MCP.

`send_message` is included deliberately, even though it has a side effect
(a simulated one). A harness that permission-gates tool calls will prompt
before running it and pass the read-only three straight through -- the same
distinction `patterns/human_in_the_loop` draws in-graph, enforced here by
the harness instead. That contrast is the point.

Run it:

    uv run --group mcp python -m shared.tools.mcp_server

Then point a harness at that command. Every MCP-speaking harness takes a
command plus args; the exact config key differs per harness and moves often
enough that this repo deliberately doesn't paste snippets -- check the
harness's current docs.
"""

from __future__ import annotations

from mcp.server import MCPServer

from shared.tools.basic import calculator, search_docs, send_message, word_count

mcp = MCPServer(
    name="agentic-design-patterns-tools",
    instructions=(
        "Tools from the agentic-design-patterns repo: safe arithmetic, a small "
        "documentation glossary, word counting, and a simulated message send."
    ),
)


# Thin wrappers rather than an adapter layer. The underlying objects are
# LangChain `BaseTool`s, and `langchain-mcp-adapters` bridges the *other*
# direction (MCP -> LangChain), so a handful of explicit functions is both
# simpler and easier to read than anything generic. MCPServer builds each
# tool's JSON schema from these type hints and docstrings.
@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. "(12 + 8) * 3".

    Parses with `ast` rather than `eval`, and bounds the cost of
    exponentiation, so it cannot become arbitrary code execution.
    """
    return calculator.invoke({"expression": expression})


@mcp.tool()
def search_documentation(query: str) -> str:
    """Look up a term in this repo's small built-in glossary of agent concepts."""
    return search_docs.invoke({"query": query})


@mcp.tool()
def count_words(text: str) -> str:
    """Count the words in a piece of text."""
    return word_count.invoke({"text": text})


@mcp.tool()
def send_a_message(recipient: str, body: str) -> str:
    """Send a message to someone. Simulated -- nothing leaves the process.

    This is the one tool here with a side effect. A harness that gates
    effectful tools should ask before running it.
    """
    return send_message.invoke({"recipient": recipient, "body": body})


if __name__ == "__main__":
    mcp.run(transport="stdio")
