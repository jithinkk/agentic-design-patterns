# Architecture Overview

This page is the cross-pattern view: how to pick between the six patterns,
how their cost/latency/risk profiles compare, and how they relate to each
other structurally. Each pattern's own README (linked below) goes deep on
that pattern specifically — where it fits, where it doesn't, architectural
tradeoffs, production infra, and relevant open-source components.

- [`prompt_chaining`](../patterns/prompt_chaining/README.md)
- [`routing`](../patterns/routing/README.md)
- [`parallelization`](../patterns/parallelization/README.md)
- [`orchestrator_workers`](../patterns/orchestrator_workers/README.md)
- [`evaluator_optimizer`](../patterns/evaluator_optimizer/README.md)
- [`react_agent`](../patterns/react_agent/README.md)

## How to choose a pattern

The decision that matters most is **how much of the control flow can you
write in code versus how much has to be decided by the model at runtime**.
Everything else follows from that:

```mermaid
flowchart TD
    A[What shape is the task?] --> B{Is the number and order\nof steps knowable in advance?}
    B -->|No — the model must decide,\nturn by turn, what to do next| Agent[react_agent]
    B -->|Yes| C{Do later steps depend on\nan earlier step's output?}

    C -->|Yes, a linear dependency chain| D{Fixed number of steps?}
    D -->|Yes| PC[prompt_chaining]
    D -->|No — needs iterative refinement\nagainst explicit criteria| EO[evaluator_optimizer]

    C -->|No, steps are independent of each other| E{Do all inputs go through\nthe same steps?}
    E -->|No — different inputs need\ndifferent handling| RT[routing]
    E -->|Yes — same steps, different\nindependent aspects| F{Is the number of parallel\nbranches fixed in code?}
    F -->|Yes| PAR[parallelization]
    F -->|No — the model decides\nbranch count at runtime| OW[orchestrator_workers]
```

A rule of thumb that follows from this tree: **prefer the most constrained
pattern that still solves the problem.** Every step down toward
`react_agent` trades away a compile-time guarantee (bounded latency,
bounded cost, a fixed set of code paths to test) for more flexibility. Only
pay for that flexibility where the task genuinely needs it — most
"we need an agent" requests turn out to be routing or orchestrator-workers
in disguise, and both are cheaper to run and easier to keep correct.

## Comparison

| Pattern | Latency profile | Cost profile | Predictability | Primary production risk |
|---|---|---|---|---|
| `prompt_chaining` | sum of step latencies | linear in step count | high — one fixed path | an early bad step cascades downstream (mitigated by the gate) |
| `routing` | +1 classification call, then one handler | low–medium | high per branch | misclassification is a silent failure — no automatic detection |
| `parallelization` | max(branch latencies) | sum of branch costs | high | partial branch failure, shared rate limits under concurrent fan-out |
| `orchestrator_workers` | orchestrator + max(worker latencies) | sum over N workers, N is runtime-decided | low — N is dynamic | unbounded fan-out cost/latency if subtask count isn't capped |
| `evaluator_optimizer` | up to `2 × max_iterations` calls | up to `2 × max_iterations` calls | medium — bounded by the cap | non-convergence; a correlated blind spot between generator and evaluator |
| `react_agent` | unbounded turns | unbounded | low — no compile-time bound | unbounded loops, tool misuse, side effects with no built-in approval gate |

The first five rows are what Anthropic's post calls **workflows** —
graphs whose shape is fixed in code even though individual node outputs
are model-generated. `react_agent` is the one **agent** in this repo: the
model itself chooses the graph's path through tool calls, not just the
content of each step. That distinction — fixed control flow vs.
model-chosen control flow — is the single biggest predictor of how hard a
pattern is to test, cap the cost of, and run safely unattended.

## Structural relationships between the patterns

A few of these patterns are more closely related than the flat list
suggests:

- **`parallelization` vs. `orchestrator_workers`** — structurally almost
  identical (fan-out, then fan-in through a reducer). The only difference
  is *when* the branch list is known: at graph-build time
  (`parallelization`, plain edges) vs. at run time
  (`orchestrator_workers`, `Send`). If you start with `parallelization`
  and find yourself wanting a variable number of branches, that's the
  upgrade path — not a rewrite.
- **`evaluator_optimizer` vs. `prompt_chaining`** — both are linear, but
  `evaluator_optimizer` adds a cycle (revise-until-pass) where
  `prompt_chaining` only ever moves forward. `prompt_chaining`'s gate is a
  one-shot version of the same idea: a checkpoint that can stop the chain,
  just without looping back to fix the problem.
- **`routing` vs. `react_agent`** — routing is a single, one-shot decision
  among a fixed set of branches; `react_agent` is the same kind of
  decision (what should happen next?) made repeatedly, informed by
  intermediate results, with no fixed branch set. A `react_agent` with
  tool calls disabled after the first turn degenerates into `routing`.
- **`orchestrator_workers` vs. `react_agent`** — both let the model decide
  something at runtime that a workflow would otherwise hardcode, but
  `orchestrator_workers` constrains that decision to "how should this one
  task be split into parallel, independent pieces?" while `react_agent`'s
  model can decide the entire trajectory, serially, with no such
  constraint. `orchestrator_workers` is meaningfully easier to bound and
  reason about as a result.

## Notes that apply across every pattern

A few production concerns aren't specific to any one pattern and are
worth calling out once:

- **Structured output over free-text parsing.** Every `_fake_responder`
  in this repo returns plain strings that node functions parse with
  string ops or light regex — that's fine for a deterministic offline
  demo, but a real implementation should use tool calling / JSON schema
  (`with_structured_output`, `instructor`, etc.) wherever a node's output
  feeds control flow (a category, a subtask list, a pass/fail verdict).
  Free-text parsing of control-flow-relevant output is a recurring
  source of production bugs in agentic systems.
- **Observability.** Because every pattern here is a named graph of named
  nodes, per-node tracing (LangSmith, or OpenTelemetry via
  `opentelemetry-instrumentation-langchain`) is close to free to add and
  disproportionately valuable — "which node degraded" is almost always
  the first question in an incident.
- **Checkpointing.** None of the graphs in this repo persist state
  (they're built fresh, in-memory, per `invoke()` call). Any pattern with
  more than one LLM call benefits from a LangGraph checkpointer
  (`SqliteSaver` for local/dev, `PostgresSaver` or a Redis-backed saver
  for production) so a mid-run crash doesn't mean re-paying for every
  step that already succeeded.
- **Model selection per node, not per graph.** Nothing forces every node
  in a graph to use the same model. Classification/routing steps, cheap
  worker subtasks, and evaluators often do fine on a smaller/cheaper
  model, while the final synthesis or the generator in
  `evaluator_optimizer` may warrant the strongest model available — this
  is one of the most effective and most underused cost levers in
  multi-step LLM systems.

## Resources

- [Building Effective Agents (Anthropic)](https://www.anthropic.com/research/building-effective-agents) — the taxonomy this repo follows
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph persistence / checkpointers](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph human-in-the-loop (`interrupt`)](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
