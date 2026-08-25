# Harnesses and Loops

The six workflow/agent patterns in this repo are graph shapes: how nodes
connect, when they branch, when they loop. This page is about the layer
above that — how a real coding agent (Claude Code, and agent harnesses
like it) wraps those shapes into something that runs safely, for hours,
across sessions, with a human able to step in. It's the "so what does this
look like outside a demo repo" page.

## Two words, precisely

**The agent loop** is the literal cycle: observe the current state, decide
what to do next, act, observe the result, repeat until done. It's old —
this is the [ReAct](https://arxiv.org/abs/2210.03629) idea from 2022 — and
it's small enough to fit in one graph.
[`react_agent`](https://github.com/jithinkk/agentic-design-patterns/tree/main/patterns/react_agent)
*is* this loop, about as bare as it gets: one node calls the model, a
conditional edge checks for a tool call, a tool node runs it, and control
returns to the model. Nothing else.

**The harness** is everything wrapped around that loop that a bare
`while True: call_model()` doesn't give you for free: what tools exist and
what they're allowed to touch, how a human gets a say before something
irreversible happens, how the agent keeps working when a single context
window isn't enough, how a big task gets split across many loops running
at once instead of one. A harness can run the same underlying loop a
thousand times with a thousand different sets of scaffolding around it.

This distinction matters because **the loop is what these six-now-seven
patterns implement, and the harness is what production agent systems
build around them.** Confusing the two is why "just add a while loop" and
"build a production coding agent" sound like the same problem and aren't.

## What a real harness adds around the loop

A few concrete, sourced examples of what sits between "the model wants to
call a tool" and "the tool call actually runs" in a real system:

- **The harness executes tools, never the model directly.** The model
  returns a *structured* tool call; the harness validates the schema,
  checks permissions, executes, and injects the result back into the
  loop. This is the mechanism that stops a prompt injection from becoming
  arbitrary code execution — the model can *ask* for anything, but only
  the harness decides what actually runs. `human_in_the_loop`'s approval
  gate in this repo is a small, explicit version of exactly this checkpoint.
- **Hooks stack into dispatchers, dispatchers into skills, skills into
  agents, agents into workflows.** Claude Code's own architecture is
  documented as roughly 30 lifecycle events (hooks) that compose this
  way — the loop stays the same shape at every layer, but each layer adds
  a place to intervene before or after a step.
- **Subagents get their own clean context window.** A parent agent
  dispatches a scoped task to a subagent, which explores deeply in
  isolation and returns a compact summary — not its full transcript —
  to the parent. `orchestrator_workers` in this repo is the graph-level
  version of this: fan out to N workers, each gets only its own subtask,
  the synthesizer sees only their results, not their internal reasoning.
  In 2026, Claude Code extended this with *dynamic* orchestration — the
  model generates orchestration scripts that fan out to tens or hundreds
  of parallel subagents with adversarial verification between them,
  rather than a fixed, code-defined worker count.
- **Long-running work survives context-window boundaries.** Anthropic's
  documented approach for multi-session agent work: an initializer agent
  sets up the environment once and writes a structured task list; a
  coding agent is then woken up repeatedly, each session making
  incremental progress, running tests, leaving a progress note for the
  *next* session, and committing. The mechanism underneath is the same
  one `human_in_the_loop` uses here for a single pause — a checkpointer
  persisting state between separate `invoke()` calls — just used across
  days instead of across one approval.

## Where each pattern shows up in a real harness

| Pattern | What it looks like inside a real agent harness |
|---|---|
| `react_agent` | The core loop itself — every tool-calling agent harness runs some version of this underneath everything else |
| `human_in_the_loop` | The permission/approval layer — Claude Code's own tool-permission prompts are this exact mechanism |
| `orchestrator_workers` | Subagent dispatch with isolated context — Claude Code's `Task` tool and its dynamic parallel-subagent orchestration |
| `parallelization` | Independent tool calls issued in a single turn, or independent checks (lint + test + typecheck) run concurrently |
| `routing` | The dispatch/classification layer that decides which skill, subagent, or specialized prompt handles a request |
| `evaluator_optimizer` | Self-verification loops — a harness re-checking its own output, or the "adversarial verification" step between parallel subagents |
| `prompt_chaining` | A fixed multi-step pipeline a harness runs for one well-defined job (e.g. a slash command with several deterministic stages) |

None of these patterns are *replaced* by harness concepts — they're the
pieces a harness assembles. A harness is not an eighth pattern; it's the
composition of these seven (plus the gaps below) into something that runs
unattended, safely, for longer than one context window.

## The gap this repo doesn't close yet: context engineering

Anthropic's own current guidance names three techniques for the problem
every long-running agent eventually hits — the context window filling up
with stale or irrelevant history:

- **Compaction** — summarize a conversation nearing its context limit and
  reinitiate with the summary, maximizing recall first, then trimming for
  precision.
- **Structured note-taking** — the agent writes notes to storage outside
  the context window and pulls them back in later, cheap persistent memory
  without keeping everything in-context.
- **Sub-agent isolation** — already covered above; it's a context-engineering
  technique as much as an orchestration one, since its real benefit is
  keeping the parent's context window clean.

`react_agent`'s `messages` list in this repo grows without bound — no
compaction, no trimming, no external notes. That's a known, documented gap
(see its README's "production readiness" section), and it's the most
consequential one left: every source consulted for this page treats
context engineering as the dominant challenge in production agents once
tool use and multi-step reasoning are in play, more than pattern choice
itself. It's the natural next pattern to add here, not yet built.

## Sources

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the original loop
- [Building Effective AI Agents (Anthropic, Dec 2024)](https://www.anthropic.com/engineering/building-effective-agents) — the taxonomy this repo's other six patterns follow
- [Effective context engineering for AI agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — compaction, structured note-taking, sub-agent architectures
- [Effective harnesses for long-running agents (Anthropic)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — the initializer-agent / coding-agent / progress-artifact pattern for multi-session work
- [Harness engineering for coding agent users (Martin Fowler)](https://martinfowler.com/articles/harness-engineering.html)
- [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) — curated list of harness engineering tools and patterns
