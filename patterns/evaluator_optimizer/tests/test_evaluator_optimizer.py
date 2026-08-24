from patterns.evaluator_optimizer.graph import build_graph


def test_loop_revises_until_it_passes():
    app = build_graph()
    result = app.invoke(
        {
            "task": "Write a tagline for Nimbus.",
            "criteria": "Must mention 'Nimbus' and be a maximum of 8 words.",
        }
    )

    assert result["passed"] is True
    assert result["iteration"] == 2  # fails once, then the feedback-informed rewrite passes
    assert "nimbus" in result["solution"].lower()
    assert result["feedback"] == "PASS"


def test_gives_up_after_max_iterations_when_it_never_passes():
    app = build_graph()
    result = app.invoke(
        {
            "task": "Write a tagline.",
            # An unsatisfiable word budget: the revised draft always adds the
            # required keyword plus three more words, which will never fit.
            "criteria": "Must mention 'Zephyr' and be a maximum of 1 words.",
            "max_iterations": 2,
        }
    )

    assert result["iteration"] == 2
    assert result["passed"] is False
