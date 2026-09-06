from dotenv import load_dotenv

load_dotenv()

from patterns.orchestrator_workers.graph import build_graph  # noqa: E402
from shared.render import block, header, step, truncate  # noqa: E402

DEFAULT_TASK = "Write a short product report covering pricing, onboarding, and support quality."


def main(task: str = DEFAULT_TASK) -> dict:
    app = build_graph()
    return app.invoke({"task": task})


def render(result: dict) -> str:
    """Narrate the dynamic fan-out: the orchestrator LLM decides the
    subtask *count* at runtime, then one `Send("worker", ...)` per subtask
    runs in parallel, each worker seeing only its own slice of state."""
    subtasks = result["subtasks"]
    by_subtask = {r["subtask"]: r["result"] for r in result["worker_results"]}

    lines = [
        header("orchestrator-workers", "orchestrator picks the subtask count at runtime → dynamic fan-out via Send"),
        step(f"1. orchestrator (LLM)  → planned {len(subtasks)} subtasks: {'; '.join(subtasks)}"),
        step(f"2. fan-out via Send    → {len(subtasks)} worker runs in parallel (each sees only its own subtask)"),
    ]
    for name in subtasks:
        lines.append(step(f"{name:<18} → {truncate(by_subtask.get(name, '(no result)'), 60)}", indent=6, bullet="•"))
    lines.append(step("3. synthesizer (LLM)  → final_report  (worker results merged via the operator.add reducer)"))
    lines.append(block("final report", result["final_report"]))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    print(render(main(task)))
