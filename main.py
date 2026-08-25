"""CLI entry point: list and run the LangGraph agentic-pattern prototypes.

    python main.py list
    python main.py run react-agent "What is (12 + 8) * 3?"

With no OPENAI_API_KEY / ANTHROPIC_API_KEY set, every pattern runs against
the built-in offline FakeChatModel (see shared/llm/fake.py) so this works
out of the box. Set LLM_PROVIDER=openai|anthropic (plus the matching API
key) to run a pattern against a real model instead.

These graphs are demos of seven patterns' *shape*, not production
systems -- see docs/harnesses-and-loops.md for how each one relates to a
real agent harness, and for memory/guardrails/MCP tool integration/evals,
the production infrastructure these graphs don't provide on their own.
"""

from __future__ import annotations

import importlib
import os
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.pretty import pprint

load_dotenv()

app = typer.Typer(help="Run working LangGraph prototypes of the classic agentic design patterns.")
console = Console()

PATTERNS = {
    "prompt-chaining": "patterns.prompt_chaining.run",
    "routing": "patterns.routing.run",
    "parallelization": "patterns.parallelization.run",
    "orchestrator-workers": "patterns.orchestrator_workers.run",
    "evaluator-optimizer": "patterns.evaluator_optimizer.run",
    "react-agent": "patterns.react_agent.run",
    "human-in-the-loop": "patterns.human_in_the_loop.run",
}


@app.command("list")
def list_patterns() -> None:
    """List the available pattern names."""
    for name, module_path in PATTERNS.items():
        console.print(f"[bold cyan]{name}[/bold cyan]  ({module_path})")


@app.command("run")
def run_pattern(
    pattern: str = typer.Argument(..., help=f"One of: {', '.join(PATTERNS)}"),
    input: Optional[str] = typer.Argument(
        None, help="Task/question text; each pattern falls back to a sensible default."
    ),
) -> None:
    """Run a pattern's graph end-to-end and print the resulting state."""
    if pattern not in PATTERNS:
        console.print(f"[red]Unknown pattern {pattern!r}.[/red] Try one of: {', '.join(PATTERNS)}")
        raise typer.Exit(1)

    module = importlib.import_module(PATTERNS[pattern])
    result = module.main(input) if input else module.main()

    provider = os.getenv("LLM_PROVIDER", "auto (fake unless an API key is set)")
    console.print(f"\n[bold green]LLM provider:[/bold green] {provider}\n")
    pprint(result)


if __name__ == "__main__":
    app()
