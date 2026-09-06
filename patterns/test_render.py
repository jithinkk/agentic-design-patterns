"""Every pattern's `run.py` exposes a `render(result) -> str` that narrates
its mechanic. `main.py run` prints it by default, so a broken `render` is a
broken CLI. These checks stay deliberately shallow -- exact wording lives in
each `run.py` -- but they pin the contract and the load-bearing keyword.
"""

import importlib

import pytest

# pattern module, substring that proves render narrated the *mechanic*
CASES = [
    ("patterns.prompt_chaining.run", "gate"),
    ("patterns.routing.run", "dispatch"),
    ("patterns.parallelization.run", "fan-in"),
    ("patterns.orchestrator_workers.run", "fan-out via Send"),
    ("patterns.evaluator_optimizer.run", "iteration"),
    ("patterns.react_agent.run", "tool call"),
    ("patterns.human_in_the_loop.run", "approval gate"),
]


@pytest.mark.parametrize("module_path, needle", CASES)
def test_render_narrates_the_mechanic(module_path, needle):
    module = importlib.import_module(module_path)
    trace = module.render(module.main())

    assert isinstance(trace, str) and trace.strip()
    assert "─" * 10 in trace  # the shared header rule
    assert needle in trace
