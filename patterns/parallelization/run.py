from dotenv import load_dotenv

load_dotenv()

from patterns.parallelization.graph import build_graph  # noqa: E402

DEFAULT_TEXT = (
    "The new release is amazing and the team loves how fast it ships. "
    "Onboarding docs still need work, but overall support has been excellent."
)


def main(text: str = DEFAULT_TEXT) -> dict:
    app = build_graph()
    return app.invoke({"text": text})


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or DEFAULT_TEXT
    result = main(text)
    print(result["report"])
