from dotenv import load_dotenv

load_dotenv()

from patterns.routing.graph import build_graph  # noqa: E402
from patterns.routing.nodes import CATEGORIES  # noqa: E402
from shared.render import block, header, step  # noqa: E402

DEFAULT_QUERY = "I was charged twice for my subscription this month, can you refund one?"


def main(query: str = DEFAULT_QUERY) -> dict:
    app = build_graph()
    return app.invoke({"query": query})


def render(result: dict) -> str:
    """Narrate the routing: 1 cheap classify call picks 1 of N specialized
    handlers; the other handlers never run."""
    chosen = result["category"]
    skipped = [c for c in CATEGORIES if c != chosen]

    return "\n".join(
        [
            header("routing", f"classify → dispatch to 1 of {len(CATEGORIES)} specialized handlers"),
            step(f"1. classify (LLM)       → {chosen!r}"),
            step(f"2. route                → {chosen}_handler   (skipped: {', '.join(skipped)})"),
            step(f"3. {chosen}_handler (LLM) → response"),
            block("response", result["response"]),
        ]
    )


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or DEFAULT_QUERY
    print(render(main(query)))
