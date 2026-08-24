# Agentic Design Patterns — LangGraph Prototypes

Working, tested LangGraph implementations of the six agentic design
patterns from Anthropic's ["Building Effective
Agents"](https://www.anthropic.com/research/building-effective-agents):
five fixed **workflows** (prompt chaining, routing, parallelization,
orchestrator-workers, evaluator-optimizer) and one open-ended **agent**
loop (ReAct). Each pattern is a small, self-contained LangGraph
`StateGraph` you can read start to finish in a couple of minutes, run from
the CLI, and poke at in tests — the goal is to understand each pattern
*inside out*, not to ship a framework.

Every pattern runs and is unit-tested **with no API key and no network
access**, against a small deterministic fake chat model. Point it at a
real model with one environment variable when you want to.

## Patterns

| Pattern | Shape | What it shows |
|---|---|---|
| [`prompt_chaining`](patterns/prompt_chaining) | linear chain + a gate | decomposing a task into sequential LLM calls with a programmatic checkpoint between them |
| [`routing`](patterns/routing) | classify → dispatch | sending different inputs to specialized prompts instead of one generic one |
| [`parallelization`](patterns/parallelization) | fan-out → fan-in | running independent LLM calls concurrently and joining the results |
| [`orchestrator_workers`](patterns/orchestrator_workers) | dynamic fan-out via `Send` | when the *number* of parallel subtasks is decided by the model at runtime |
| [`evaluator_optimizer`](patterns/evaluator_optimizer) | generate ⇄ evaluate loop | iterative refinement against explicit pass/fail criteria |
| [`react_agent`](patterns/react_agent) | tool-call loop | the open-ended "agent": the model decides whether to act or answer, turn by turn |

Each pattern's own README has its graph diagram and an explanation of why
that shape fits that pattern. Start with `prompt_chaining` (simplest) and
end with `react_agent` (least predictable).

## Quick start

Requires Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run main.py list
uv run main.py run react-agent "What is (12 + 8) * 3?"
uv run main.py run prompt-chaining "Why LangGraph is a good fit for agents"
```

Or activate the venv and use `python` directly:

```bash
source .venv/bin/activate
python main.py run evaluator-optimizer "Write a tagline for Nimbus"
python -m patterns.orchestrator_workers.run "Write a report covering pricing, onboarding, and support quality."
```

## Running against a real model

By default every pattern uses `shared/llm/fake.py`'s `FakeChatModel` — a
scripted stand-in that lets the whole repo run offline. To use a real
model instead, set an API key and, optionally, `LLM_PROVIDER`:

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY=sk-...
export LLM_PROVIDER=anthropic         # or "openai"; auto-detected from the key if omitted
uv run main.py run react-agent "What's a good LangGraph pattern for a support bot?"
```

See `shared/llm/factory.py` for provider selection and `ANTHROPIC_MODEL` /
`OPENAI_MODEL` overrides.

## Testing

```bash
uv run pytest            # every pattern, all offline
uv run pytest patterns/orchestrator_workers -v
```

## Project layout

```
agentic-design-patterns/
├── main.py                        # Typer CLI: list/run patterns
├── patterns/
│   ├── prompt_chaining/
│   ├── routing/
│   ├── parallelization/
│   ├── orchestrator_workers/
│   ├── evaluator_optimizer/
│   └── react_agent/
│       ├── graph.py                # StateGraph wiring: nodes + edges
│       ├── nodes.py                # node functions + the fake-LLM script for this pattern
│       ├── run.py                  # `main()` + CLI entry point
│       ├── tests/test_*.py         # deterministic end-to-end tests
│       └── README.md               # pattern-specific diagram + notes
└── shared/
    ├── llm/
    │   ├── factory.py               # get_chat_model(provider=...) — fake / openai / anthropic
    │   └── fake.py                  # FakeChatModel: scripted BaseChatModel, no network needed
    └── tools/
        └── basic.py                 # calculator, search_docs, word_count (used by react_agent)
```

Every pattern follows the same shape: `graph.py` defines the `StateGraph`
and its edges, `nodes.py` holds the node functions (each backed by
`shared.llm.factory.get_chat_model`), `run.py` exposes a `main(...)`
function the CLI calls into, and `tests/` exercises the graph end to end
against the fake LLM.

### Adding a new pattern

1. `mkdir -p patterns/<name>/tests` with `__init__.py` files.
2. Write `nodes.py`: node functions plus a `_fake_responder` that gives
   deterministic behavior for tests (see any existing pattern for the
   shape), wired up via `get_chat_model(responder=_fake_responder)`.
3. Write `graph.py`: a `TypedDict` state and a `build_graph()` that wires
   nodes with `add_edge` / `add_conditional_edges`.
4. Write `run.py` with a `main(...)` function and a CLI-runnable
   `if __name__ == "__main__"` block.
5. Add tests in `tests/test_<name>.py` and register the pattern in
   `main.py`'s `PATTERNS` dict.

## Resources

- [Building Effective Agents (Anthropic)](https://www.anthropic.com/research/building-effective-agents) — the taxonomy this repo follows
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
