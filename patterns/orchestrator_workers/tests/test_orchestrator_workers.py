from patterns.orchestrator_workers.graph import build_graph


def test_dynamic_fan_out_covers_every_subtask():
    app = build_graph()
    task = "Write a short product report covering pricing, onboarding, and support quality."
    result = app.invoke({"task": task})

    assert result["subtasks"] == ["pricing", "onboarding", "support quality"]
    assert len(result["worker_results"]) == 3

    covered = {r["subtask"] for r in result["worker_results"]}
    assert covered == set(result["subtasks"])

    assert result["final_report"].startswith("# Final Report")
    for subtask in result["subtasks"]:
        assert subtask in result["final_report"]


def test_falls_back_to_default_topics_without_a_covering_clause():
    app = build_graph()
    result = app.invoke({"task": "Write a brief status update."})

    assert result["subtasks"] == ["an overview", "key considerations"]
    assert len(result["worker_results"]) == 2
