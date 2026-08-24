from dotenv import load_dotenv

load_dotenv()

from patterns.evaluator_optimizer.graph import build_graph  # noqa: E402

DEFAULT_TASK = "Write a one-line product tagline for a note-taking app called Nimbus."
DEFAULT_CRITERIA = "Must mention 'Nimbus' and be a maximum of 8 words."


def main(task: str = DEFAULT_TASK, criteria: str = DEFAULT_CRITERIA) -> dict:
    app = build_graph()
    return app.invoke({"task": task, "criteria": criteria})


if __name__ == "__main__":
    result = main()

    print(f"Solution after {result['iteration']} iteration(s): {result['solution']}")
    print("Evaluator verdict:", result["feedback"])
    print("Passed:", result["passed"])
