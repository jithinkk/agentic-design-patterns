from dotenv import load_dotenv

load_dotenv()

from patterns.prompt_chaining.graph import build_graph  # noqa: E402

DEFAULT_TOPIC = "Why LangGraph is a good fit for building agentic workflows"


def main(topic: str = DEFAULT_TOPIC) -> dict:
    app = build_graph()
    return app.invoke({"topic": topic})


if __name__ == "__main__":
    import sys

    topic = " ".join(sys.argv[1:]) or DEFAULT_TOPIC
    result = main(topic)

    print("Outline:\n" + result["outline"])
    print("\nGate:", result["gate_reason"])
    if result.get("gate_passed"):
        print("\nFinal:\n" + result["final"])
    else:
        print("\nChain stopped at the gate; no draft was generated.")
