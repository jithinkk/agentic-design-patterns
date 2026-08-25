# Real-World Examples

[`architecture-overview.md`](architecture-overview.md)'s decision tree
gives the decision logic for picking a pattern. This page applies it to
concrete scenarios end to end — one worked example per pattern, plus two
cases where the tempting first choice turns out to be wrong. Each example
follows the same shape: the scenario, the alternative that looks
plausible at first glance, why the tree actually routes elsewhere, and
the trade-off accepted by going with it.

## One example per pattern

### `prompt_chaining` — turning a draft into a published doc

A content team publishes long-form docs through a fixed pipeline: outline
the structure, draft the body from the outline, edit for tone and length,
then fact-check the final draft. Each step consumes the previous step's
output directly, in a fixed order that never changes.

**Tempting alternative:** one big prompt asking for "a polished, fact-checked
doc" in a single call. It saves round-trips, but a single call has to hold
structure, prose quality, and factual accuracy in mind simultaneously —
in practice it does all three worse than four calls that each focus on
one job.

**Why `prompt_chaining` fits:** the number and order of steps are known
up front, and each step strictly depends on the one before it — exactly
the "fixed number of steps, linear dependency chain" branch of the
decision tree.

**Trade-off accepted:** total latency is the sum of all four steps, and
an early bad step (a bad outline) cascades downstream unless a gate
catches it.

### `routing` — support ticket intake

A support platform classifies incoming tickets into billing, technical,
or account-closure, then hands each to a differently-tuned prompt with
its own tone and its own tool access (billing tickets can look up
invoices; technical tickets can search a knowledge base).

**Tempting alternative:** a single `react_agent` that reads the ticket
and decides what to do turn by turn. It would work, but the "what kind of
ticket is this" decision only ever needs to be made once, up front — every
ticket in this system takes exactly one classify-then-handle path, not an
open-ended trajectory.

**Why `routing` fits:** inputs fall into a fixed, known set of categories,
each better served by a focused handler than one generic prompt — the
tree's "different inputs need different handling" branch.

**Trade-off accepted:** misclassification is a silent failure with no
automatic detection — a ticket routed to the wrong handler just gets a
wrong-flavored response, not an error.

### `parallelization` — content moderation

A moderation pipeline runs three independent checks on every submission —
a safety check, a PII check, a tone check — then combines the three
verdicts into one decision.

**Tempting alternative:** run the checks as a `prompt_chaining` sequence,
one after another. Cheaper to write, but the checks don't depend on each
other's output at all — chaining them only adds latency for no benefit.

**Why `parallelization` fits:** the same input goes through a fixed,
known number of independent branches evaluated separately and combined
afterward — the tree's "same steps, different independent aspects, fixed
branch count" path.

**Trade-off accepted:** total cost is the sum of all three branches (not
the max), and a partial branch failure has to be handled explicitly —
there's no single call to just retry.

### `orchestrator_workers` — repo-wide migration

A migration tool inspects a codebase, decides how many files actually
need a particular change, and dispatches one worker per affected file.

**Tempting alternative:** `parallelization` — it looks identical from a
distance (fan out, then fan in), but the branch count here isn't knowable
until the model has actually inspected the repo. A `parallelization` graph
needs its branch list fixed at graph-build time; this task can't supply
one until runtime.

**Why `orchestrator_workers` fits:** the model decides the number of
parallel subtasks at runtime rather than the graph fixing it in code —
the tree's explicit distinction between `parallelization` and
`orchestrator_workers`.

**Trade-off accepted:** cost and latency are only as predictable as the
model's own subtask count — an unbounded fan-out needs an explicit cap.

### `evaluator_optimizer` — SQL generation against a live schema

An internal analytics tool drafts a SQL query from a natural-language
question, dry-runs it against the schema, and — if it errors — revises
the query using the error message, repeating until it's valid or a retry
cap is hit.

**Tempting alternative:** `prompt_chaining` — draft, then "clean up" the
query in a second step. But a chain never loops back to fix a step based
on that step's own failure; it only ever moves forward. This task
specifically needs to revise against a concrete pass/fail signal (does
the query execute), which is a cycle, not a line.

**Why `evaluator_optimizer` fits:** there's a clear, automatic evaluation
criterion (does the dry-run succeed) and iterative refinement against it
measurably improves the result — the tree's "no fixed step count, needs
iterative refinement against explicit criteria" branch.

**Trade-off accepted:** up to `2 × max_iterations` calls in the worst
case, and non-convergence is a real failure mode if the generator and
evaluator share a blind spot.

### `react_agent` — a debugging assistant

A debugging assistant runs shell commands, reads their output, and
decides the next command based on what it just saw — narrowing in on a
root cause over an unpredictable number of turns.

**Tempting alternative:** `orchestrator_workers` — enumerate a set of
likely causes up front and dispatch a worker to check each one in
parallel. This fails because the *next* useful command depends on what
the *previous* command's output revealed; there's no static task list to
hand out at the start, only a decision that has to be made turn by turn.

**Why `react_agent` fits:** the number and order of steps genuinely can't
be known in advance, and the model has to decide what to do next based on
intermediate results — the tree's "model must decide, turn by turn" branch,
with read-only tools only.

**Trade-off accepted:** no compile-time bound on turns, cost, or latency —
p99 is fundamentally less predictable than any fixed-shape workflow above.

### `human_in_the_loop` — the same assistant, with a deploy tool

Take the debugging assistant above and give it one more tool: it can
actually push the fix it found. That single tool call — the one with a
real, hard-to-undo consequence — is gated behind human approval; every
read-only investigation step before it runs exactly as it did in the
plain `react_agent` version.

**Tempting alternative, two directions:** skip the gate entirely for
speed — fast, until the one autonomous deploy that's wrong is exactly the
irreversible mistake this pattern exists to prevent. Or gate *every* tool
call, including the read-only investigation steps — safer-looking, but it
kills the agent's autonomy for the 95% of steps that carry no real risk
(see `human_in_the_loop/README.md`'s own "Where not to use it" note on
this exact failure mode).

**Why `human_in_the_loop` fits:** the agent has at least one tool with a
real-world, hard-to-undo consequence — the tree's "calls tools with
real-world side effects" branch, gating only that tool rather than the
whole loop.

**Trade-off accepted:** latency becomes human-paced for the gated call,
and a stuck, never-resumed approval blocks the run forever unless a
timeout policy is added.

## When the reasoning goes wrong

The rule of thumb in `architecture-overview.md` — prefer the most
constrained pattern that still solves the problem — cuts both ways.
Over-reaching for flexibility you don't need is one mistake; so is
under-fitting a pattern that's outgrown its constraints.

**Over-reaching:** a team defaults to a full `react_agent` for a weekly
report job. The job is, in practice, always the same three steps in the
same order: pull last week's metrics, summarize them, format the summary
as an email. Nothing about the task ever varies — but because it's
"an agent task," it gets built as one. The result pays every cost of
`react_agent` (unbounded latency, unbounded turns, three failure surfaces
to test instead of one fixed path) and gets nothing back for it, because
the flexibility an agent buys was never actually needed. `prompt_chaining`
would have been cheaper, faster, and fully testable against three fixed
inputs.

**Under-reaching:** a team builds a `routing` classifier for ticket type
with a fixed set of branches — billing, technical, account-closure. Six
months later, the branch list has grown to eleven, with a new one added
by hand roughly every month as the product surface grows. That pattern of
change is itself the signal: the branch set was never actually fixed, it
was just small enough not to notice. Either `orchestrator_workers` (let
the model decide how many categories apply to a given ticket, if handling
per category stays a fixed shape) or `react_agent` (if the handling itself
also needs to be open-ended) fits the system this has actually become
better than continuing to hand-add branches to a `routing` table.

## See also

- [`architecture-overview.md`](architecture-overview.md) — the decision
  tree and comparison table these examples apply. Use the tree to narrow
  down a pattern, use this page to sanity-check the reasoning against a
  concrete case.
- [`harnesses-and-loops.md`](harnesses-and-loops.md) — how these patterns
  show up inside a real agent harness, beyond this repo's demo graphs.
