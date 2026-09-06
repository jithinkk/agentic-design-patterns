from dotenv import load_dotenv

load_dotenv()

from patterns.parallelization.graph import build_graph  # noqa: E402
from shared.render import block, header, step, truncate  # noqa: E402

DEFAULT_TEXT = (
    "The new release is amazing and the team loves how fast it ships. "
    "Onboarding docs still need work, but overall support has been excellent."
)


def main(text: str = DEFAULT_TEXT) -> dict:
    app = build_graph()
    return app.invoke({"text": text})


def render(result: dict) -> str:
    """Narrate the fan-out/fan-in: 3 independent LLM calls run in one
    LangGraph superstep, then a no-LLM join once all 3 land."""
    branches = [
        ("sentiment", result["sentiment"]),
        ("summary", result["summary"]),
        ("keywords", result["keywords"]),
    ]
    lines = [header("parallelization", "fan-out 3 independent LLM calls in one superstep → fan-in join")]
    for i, (name, value) in enumerate(branches):
        bullet = "fan-out ┬" if i == 0 else ("        ├" if i < len(branches) - 1 else "        └")
        lines.append(step(f"{bullet} {name:<9} (LLM) → {truncate(value, 60)}", indent=0))
    lines.append(step("fan-in    → aggregate (no LLM) joined 3 results", indent=0))
    lines.append(block("report", result["report"]))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or DEFAULT_TEXT
    print(render(main(text)))
