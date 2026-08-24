import pytest

from patterns.routing.graph import build_graph


@pytest.mark.parametrize(
    ("query", "expected_category", "expected_marker"),
    [
        ("Why was I charged twice on my last invoice?", "billing", "[billing specialist]"),
        ("The app crashes with an exception on startup.", "technical", "[technical specialist]"),
        ("What are your support hours?", "general", "[general support]"),
    ],
)
def test_routes_to_the_right_specialist(query, expected_category, expected_marker):
    app = build_graph()
    result = app.invoke({"query": query})

    assert result["category"] == expected_category
    assert expected_marker in result["response"]
