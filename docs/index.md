# Agentic Design Patterns

Working, tested LangGraph implementations of the six agentic design
patterns from Anthropic's ["Building Effective
Agents"](https://www.anthropic.com/research/building-effective-agents) —
five fixed **workflows** and one open-ended **agent** loop — plus a
seventh, **human-in-the-loop**. Each pattern is a small, self-contained
LangGraph `StateGraph` you can read start to finish in a couple of
minutes, run from the CLI, and poke at in tests.

!!! tip "No API key required"
    Every pattern runs and is unit-tested **offline**, against a small
    deterministic fake chat model. Point it at a real model with one
    environment variable when you want to — see
    [Running against a real model](#running-against-a-real-model) below.

[:octicons-rocket-24: Quick start](#quick-start){ .md-button .md-button--primary }
[:fontawesome-brands-github: View on GitHub](https://github.com/jithinkk/agentic-design-patterns){ .md-button }

## Patterns

<div class="grid cards" markdown>

-   :material-link-variant:{ .lg .middle } **Prompt Chaining**

    ---

    Linear chain + a gate — decomposing a task into sequential LLM calls
    with a programmatic checkpoint between them.

    [:octicons-arrow-right-24: prompt_chaining](patterns/prompt_chaining.md)

-   :material-sign-direction:{ .lg .middle } **Routing**

    ---

    Classify → dispatch — sending different inputs to specialized
    prompts instead of one generic one.

    [:octicons-arrow-right-24: routing](patterns/routing.md)

-   :material-call-split:{ .lg .middle } **Parallelization**

    ---

    Fan-out → fan-in — running independent LLM calls concurrently and
    joining the results.

    [:octicons-arrow-right-24: parallelization](patterns/parallelization.md)

-   :material-sitemap:{ .lg .middle } **Orchestrator-Workers**

    ---

    Dynamic fan-out via `Send` — when the *number* of parallel subtasks
    is decided by the model at runtime.

    [:octicons-arrow-right-24: orchestrator_workers](patterns/orchestrator_workers.md)

-   :material-autorenew:{ .lg .middle } **Evaluator-Optimizer**

    ---

    Generate ⇄ evaluate loop — iterative refinement against explicit
    pass/fail criteria.

    [:octicons-arrow-right-24: evaluator_optimizer](patterns/evaluator_optimizer.md)

-   :material-robot-outline:{ .lg .middle } **ReAct Agent**

    ---

    Tool-call loop — the open-ended "agent": the model decides whether
    to act or answer, turn by turn.

    [:octicons-arrow-right-24: react_agent](patterns/react_agent.md)

-   :material-hand-back-right-outline:{ .lg .middle } **Human-in-the-Loop**

    ---

    Agent loop + approval gate — pausing before a side-effecting tool
    call until a human approves or denies it.

    [:octicons-arrow-right-24: human_in_the_loop](patterns/human_in_the_loop.md)

</div>

Start with `prompt_chaining` (simplest) and end with `human_in_the_loop`
(built on `react_agent`, least predictable plus a human in the mix). Each
pattern's own page has a Mermaid diagram of its graph plus notes on where
it fits, where it doesn't, architectural tradeoffs, production infra
choices, production readiness, and relevant open-source components.

## Beyond the patterns

<div class="grid cards" markdown>

-   :material-source-branch:{ .lg .middle } **Architecture Overview**

    ---

    The cross-pattern view: a decision tree for picking between the
    seven patterns and a latency/cost/risk comparison table.

    [:octicons-arrow-right-24: Read more](architecture-overview.md)

-   :material-cog-outline:{ .lg .middle } **Harnesses and Loops**

    ---

    How these patterns map onto real agent harnesses — Claude Code
    included — plus memory, guardrails, MCP tools, and evals.

    [:octicons-arrow-right-24: Read more](harnesses-and-loops.md)

-   :material-lightbulb-outline:{ .lg .middle } **Real-World Examples**

    ---

    The decision tree applied to concrete scenarios, including a couple
    of cases where the tempting first choice is wrong.

    [:octicons-arrow-right-24: Read more](real-world-examples.md)

-   :material-source-repository:{ .lg .middle } **Under deepagents**

    ---

    The same patterns re-expressed in LangChain's `deepagents` — what a
    framework supplies for free and what it costs you. Now lives in its
    own repo, `ai-harnesses`.

    [:octicons-arrow-right-24: Read more](https://jithinkk.github.io/ai-harnesses/deepagents/)

</div>

## Quick start

{% include-markdown "../README.md" start="## Quick start" %}
