"""A small, dependency-free toolset shared by the tool-using patterns.

Kept intentionally simple (arithmetic, an in-memory doc lookup, a word
counter) so the react_agent and orchestrator_workers prototypes can be
exercised end-to-end without any external API.
"""

from __future__ import annotations

import ast
import operator

from langchain_core.tools import tool

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '(3 + 4) * 2'."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as exc:
        return f"error: could not evaluate {expression!r} ({exc})"


_DOCS = {
    "langgraph": "LangGraph is a library for building stateful, multi-actor "
    "applications with LLMs, modeled as a graph of nodes and edges.",
    "react": "ReAct interleaves reasoning traces and actions: the model "
    "decides whether to call a tool or answer, observes the result, and repeats.",
    "orchestrator": "The orchestrator-workers pattern has a central LLM "
    "dynamically break a task into subtasks and delegate them to worker LLMs.",
    "evaluator": "The evaluator-optimizer pattern loops a generator against "
    "an evaluator that grades output and returns feedback until it passes.",
}


@tool
def search_docs(query: str) -> str:
    """Search a small built-in glossary of agentic-pattern terms."""
    query = query.lower()
    hits = [text for key, text in _DOCS.items() if key in query]
    if not hits:
        return "No matching entries found."
    return "\n".join(hits)


@tool
def word_count(text: str) -> str:
    """Count the words in a piece of text."""
    return str(len(text.split()))


ALL_TOOLS = [calculator, search_docs, word_count]
