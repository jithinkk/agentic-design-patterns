# Agentic Design Patterns — LangGraph Prototypes

Working, tested LangGraph implementations of the six agentic design
patterns from Anthropic's ["Building Effective
Agents"](https://www.anthropic.com/research/building-effective-agents):
five fixed **workflows** (prompt chaining, routing, parallelization,
orchestrator-workers, evaluator-optimizer) and one open-ended **agent**
loop (ReAct) — plus a seventh, **human-in-the-loop**, extending the agent
loop with the approval-gate mechanism every current production agent
architecture treats as required infrastructure, not optional. Each
pattern is a small, self-contained LangGraph `StateGraph` you can read
start to finish in a couple of minutes, run from the CLI, and poke at in
tests — the goal is to understand each pattern *inside out*, not to ship
a framework.

Every pattern runs and is unit-tested **with no API key and no network
access**, against a small deterministic fake chat model. Point it at a
real model with one environment variable when you want to.

## Patterns

| Pattern | Shape | What it shows |
|---|---|---|
| [`prompt_chaining`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/prompt_chaining) | linear chain + a gate | decomposing a task into sequential LLM calls with a programmatic checkpoint between them |
| [`routing`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/routing) | classify → dispatch | sending different inputs to specialized prompts instead of one generic one |
| [`parallelization`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/parallelization) | fan-out → fan-in | running independent LLM calls concurrently and joining the results |
| [`orchestrator_workers`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/orchestrator_workers) | dynamic fan-out via `Send` | when the *number* of parallel subtasks is decided by the model at runtime |
| [`evaluator_optimizer`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/evaluator_optimizer) | generate ⇄ evaluate loop | iterative refinement against explicit pass/fail criteria |
| [`react_agent`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/react_agent) | tool-call loop | the open-ended "agent": the model decides whether to act or answer, turn by turn |
| [`human_in_the_loop`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/human_in_the_loop) | agent loop + approval gate | pausing before a side-effecting tool call until a human approves or denies it |

Each pattern's own README has a Mermaid diagram of its graph plus notes on
where it fits, where it doesn't, architectural tradeoffs, production infra
choices, production readiness, and relevant open-source components. Start
with `prompt_chaining` (simplest) and end with `human_in_the_loop` (built
on `react_agent`, least predictable plus a human in the mix). For the
cross-pattern view — a decision tree for picking between them and a
latency/cost/risk comparison table — see
[`docs/architecture-overview.md`](docs/architecture-overview.md). For how
these patterns map onto real agent harnesses (Claude Code included), the
agent loop underneath them, the different harness archetypes and what
guides picking one, and what production adds beyond the graphs here —
memory, guardrails, MCP tool integration, evals — see
[`docs/harnesses-and-loops.md`](docs/harnesses-and-loops.md). For worked
examples applying the decision tree to concrete scenarios — including a
couple of cases where the tempting first choice is wrong — see
[`docs/real-world-examples.md`](docs/real-world-examples.md). For the same
patterns re-expressed in LangChain's `deepagents` — what a framework
supplies for free and what it costs you — see
[`harnesses/`](https://github.com/jithinkk/agentic-design-patterns/tree/main/harnesses).

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
python main.py run human-in-the-loop "Send a message to Alice: the report is ready."
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
├── docs/
│   ├── architecture-overview.md   # cross-pattern decision tree + comparison table
│   ├── harnesses-and-loops.md     # harnesses, memory, guardrails, MCP, evals: production vs. this repo
│   └── real-world-examples.md     # the decision tree applied to concrete scenarios
├── harnesses/
│   └── deepagents/                # the same patterns under LangChain's deepagents
├── patterns/
│   ├── prompt_chaining/
│   ├── routing/
│   ├── parallelization/
│   ├── orchestrator_workers/
│   ├── evaluator_optimizer/
│   ├── react_agent/
│   └── human_in_the_loop/
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
        └── basic.py                 # calculator, search_docs, word_count, send_message
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
- [Effective context engineering for AI agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — memory/context management this repo doesn't implement yet; see `docs/harnesses-and-loops.md`
- [Effective harnesses for long-running agents (Anthropic)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

## License

This project is licensed under the [MIT License](LICENSE).
