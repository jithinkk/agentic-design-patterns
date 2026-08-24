from langchain_core.messages import AIMessage

from patterns.prompt_chaining import nodes
from patterns.prompt_chaining.graph import build_graph
from shared.llm.factory import get_chat_model


def test_happy_path_runs_the_full_chain():
    app = build_graph()
    result = app.invoke({"topic": "LangGraph design patterns"})

    assert result["gate_passed"] is True
    assert "final" in result
    assert result["final"]
    assert "(tightened for clarity and flow)" in result["final"]


def test_gate_stops_the_chain_on_a_thin_outline(monkeypatch):
    def short_outline_responder(messages):
        return AIMessage(content="1. Just one section")

    monkeypatch.setattr(nodes, "_llm", get_chat_model(responder=short_outline_responder))

    app = build_graph()
    result = app.invoke({"topic": "A topic that yields a thin outline"})

    assert result["gate_passed"] is False
    assert "draft" not in result
    assert "final" not in result
    assert "1 section" in result["gate_reason"]
