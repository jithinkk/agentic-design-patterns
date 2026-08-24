from dotenv import load_dotenv

load_dotenv()

from patterns.orchestrator_workers.graph import build_graph  # noqa: E402

DEFAULT_TASK = "Write a short product report covering pricing, onboarding, and support quality."


def main(task: str = DEFAULT_TASK) -> dict:
    app = build_graph()
    return app.invoke({"task": task})


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    result = main(task)

    print("Subtasks:")
    for subtask in result["subtasks"]:
        print(f"  - {subtask}")
    print("\nFinal report:\n")
    print(result["final_report"])
