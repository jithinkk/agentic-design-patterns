from dotenv import load_dotenv

load_dotenv()

from patterns.evaluator_optimizer.graph import build_graph  # noqa: E402
from shared.render import block, header, step  # noqa: E402

DEFAULT_TASK = "Write a one-line product tagline for a note-taking app called Nimbus."
DEFAULT_CRITERIA = "Must mention 'Nimbus' and be a maximum of 8 words."


def main(task: str = DEFAULT_TASK, criteria: str = DEFAULT_CRITERIA) -> dict:
    app = build_graph()
    return app.invoke({"task": task, "criteria": criteria})


def render(result: dict) -> str:
    """Narrate the generate ⇄ evaluate loop: it spins until the evaluator
    passes the draft or `max_iterations` is hit. Only the final iteration's
    solution and verdict survive in state, so the earlier turns are
    summarised, not quoted."""
    turns = result["iteration"]
    passed = result["passed"]
    outcome = "accept" if passed else "give up (max_iterations reached)"

    lines = [header("evaluator-optimizer", "generate ⇄ evaluate loop until PASS or max_iterations")]
    if turns > 1:
        span = "iteration 1" if turns == 2 else f"iterations 1..{turns - 1}"
        lines.append(step(f"{span}: generate → evaluate → FAIL → revise (feedback folded back into the prompt)"))
    lines.append(step(f"iteration {turns}: generate → evaluate → {'PASS' if passed else 'FAIL'}"))
    lines.append(step(f"→ {outcome} after {turns} iteration(s)"))
    lines.append(block("final verdict", result["feedback"]))
    lines.append(block("solution", result["solution"]))
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(main()))
