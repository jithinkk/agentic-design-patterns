from dotenv import load_dotenv

load_dotenv()

from patterns.prompt_chaining.graph import build_graph  # noqa: E402
from shared.render import block, header, step  # noqa: E402

DEFAULT_TOPIC = "Why LangGraph is a good fit for building agentic workflows"


def main(topic: str = DEFAULT_TOPIC) -> dict:
    app = build_graph()
    return app.invoke({"topic": topic})


def render(result: dict) -> str:
    """Narrate the chain: 3 sequential LLM calls with a programmatic gate
    between calls 1 and 2 that can halt the run before it spends more."""
    sections = [ln for ln in result["outline"].splitlines() if ln.strip()]
    passed = result.get("gate_passed")

    lines = [
        header("prompt-chaining", "linear chain of 3 LLM calls + 1 programmatic gate"),
        step(f"1. generate_outline (LLM)   → {len(sections)}-section outline"),
        step(f"2. gate_check (no LLM)      → {'PASS' if passed else 'STOP'}: {result['gate_reason']}"),
    ]
    if passed:
        lines += [
            step("3. expand_draft (LLM)       → draft"),
            step("4. polish (LLM)             → final"),
            block("final", result["final"]),
        ]
    else:
        lines += [step("   chain halted at the gate — the 2 remaining LLM calls never ran")]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    topic = " ".join(sys.argv[1:]) or DEFAULT_TOPIC
    print(render(main(topic)))
