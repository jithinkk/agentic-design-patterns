# Harnesses

The seven patterns in [`patterns/`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns)
are written in vanilla LangGraph, and that stays the default: everything
there runs with no harness dependency installed. This directory answers a
different, narrower question — **should you hand-build a pattern, or let a
framework supply it?**

- [`deepagents/`](https://github.com/jithinkk/agentic-design-patterns/tree/main/harnesses/deepagents)
  — `orchestrator_workers` and `human_in_the_loop`, re-expressed in
  LangChain's [deepagents](https://github.com/langchain-ai/deepagents),
  side by side with their vanilla equivalents. Fully offline and tested.

Install and run:

```bash
uv sync --group harnesses
uv run python -m harnesses.deepagents.run
uv run pytest harnesses -v
```

## What is deliberately *not* here

**The patterns are not exposed as MCP tools.** It would be technically easy
and conceptually wrong. MCP exists to give an agent *capabilities* — query
this database, deploy this service. The seven patterns are *architectural
shapes*, not capabilities: a `routing` tool called from a coding agent just
runs a toy graph sorting a fake support ticket, which helps nobody and
teaches nothing about routing. (The repo's actual **tools** are a different
matter — those are genuine capabilities, and exposing them over MCP is
coherent.)

**CLI coding agents are not integrated, only documented.** OpenCode, Goose,
Hermes Agent, Crush, Cline and Aider are harnesses in their own right —
per [`docs/harnesses-and-loops.md`](https://github.com/jithinkk/agentic-design-patterns/blob/main/docs/harnesses-and-loops.md),
*"a harness is not an eighth pattern; it's the composition of these
seven."* They already use these patterns internally; feeding patterns into
them inverts the relationship. And their config surface moves fast enough
that pasted, untestable snippets would be quietly wrong within months — so
that guidance lives in prose, which can say "check the current docs," and
not in this directory, which can't be CI-verified.

**Only one framework is covered.** Nobody re-implements a single workflow
across three frameworks in production; they pick one. A second framework
would multiply maintenance without changing the lesson.

## Adding another harness

The bar, mirroring the repo's "everything runs and is tested with no API
key" guarantee:

1. It must be drivable **offline** by a stand-in model. For anything built
   on LangChain this means accepting a `BaseChatModel`, so
   `shared/llm/fake.py`'s `FakeChatModel` drops in. A harness that can only
   talk to a live endpoint belongs in docs, not here.
2. Implement only the patterns it expresses **natively**, and document the
   non-fits — those explain more than the fits do.
3. Follow the existing module conventions: `build_agent()` alongside a
   `run.py` exposing `main(...) -> dict`, and tests under `tests/` opening
   with `pytest.importorskip("<package>")` so a plain `uv sync` still gets
   a green suite.
4. Add the dependency to the `harnesses` group in `pyproject.toml` and
   regenerate `uv.lock` — CI runs `uv sync --locked` and will fail on
   drift.
