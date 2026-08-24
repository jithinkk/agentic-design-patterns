from patterns.parallelization.graph import build_graph


def test_fan_out_and_fan_in_produce_a_full_report():
    app = build_graph()
    result = app.invoke(
        {"text": "This release is great and the team loves it. Users are happy with the speed."}
    )

    assert result["sentiment"] == "positive"
    assert result["summary"]
    assert result["keywords"]
    assert "## Analysis Report" in result["report"]
    assert result["sentiment"] in result["report"]
    assert result["summary"] in result["report"]
    assert result["keywords"] in result["report"]


def test_negative_text_is_detected():
    app = build_graph()
    result = app.invoke({"text": "This update is terrible and broke everything, we are angry."})

    assert result["sentiment"] == "negative"
