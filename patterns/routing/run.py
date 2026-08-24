from dotenv import load_dotenv

load_dotenv()

from patterns.routing.graph import build_graph  # noqa: E402

DEFAULT_QUERY = "I was charged twice for my subscription this month, can you refund one?"


def main(query: str = DEFAULT_QUERY) -> dict:
    app = build_graph()
    return app.invoke({"query": query})


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or DEFAULT_QUERY
    result = main(query)

    print("Category:", result["category"])
    print("Response:", result["response"])
