# Observability — two ways to watch a pattern run

Running a pattern gives you a **narrated trace** by default. Adding
`--otel` gives you the same run as an **OpenTelemetry span tree**. They
answer different questions, and the gap between them is itself instructive.

## 1. The narrated trace (default, zero dependencies)

```console
$ uv run main.py run orchestrator-workers

orchestrator-workers · orchestrator picks the subtask count at runtime → dynamic fan-out via Send
────────────────────────────────────────────────────────────
  1. orchestrator (LLM)  → planned 3 subtasks: pricing; onboarding; support quality
  2. fan-out via Send    → 3 worker runs in parallel (each sees only its own subtask)
      • pricing            → Findings on pricing: three relevant points worth …
      • onboarding         → Findings on onboarding: three relevant points …
      • support quality    → Findings on support quality: three relevant …
  3. synthesizer (LLM)  → final_report  (worker results merged via the operator.add reducer)
```

Each pattern's `run.py` has a `render(result) -> str` that produces this.
It narrates the **mechanic** — how many LLM calls, in what shape, which
branch was taken, how many loop turns — the thing you actually want when
the goal is "understand the pattern inside out". `--raw` drops it for the
untouched state dict.

This is deliberately *not* an LLM-observability tool. It knows what
"dynamic fan-out" means; a generic tracer does not.

## 2. The OpenTelemetry span tree (`--otel`, opt-in)

```bash
uv sync --group otel
uv run main.py run orchestrator-workers --otel
```

`--otel` initialises [Traceloop's OpenLLMetry
SDK](https://github.com/traceloop/openllmetry), which auto-instruments
LangChain / LangGraph and the Anthropic / OpenAI clients and emits spans
on the [OpenTelemetry GenAI semantic
conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
`shared/obs.py` wires those spans to a **console exporter**, so the tree
prints to your terminal with no backend and no API key.

What you get is call-level, not mechanic-level: a `langgraph` root span,
one span per node execution nested under it, one `chat` span per model
call with `gen_ai.request.model`, token counts, and (unless you disable
it) the prompt and completion as span attributes.

### How the span tree lines up with each pattern

| Pattern | What the span tree shows | What only the narrated trace makes obvious |
|---|---|---|
| prompt-chaining | 4 node spans in series; 3 `chat` spans (none under `gate_check`) | that `gate_check` is a *programmatic* gate that can halt the chain |
| routing | a `classify` span, then exactly one handler span | that the other two handlers were never entered |
| parallelization | 3 node spans with overlapping start/end under one superstep | that they share a superstep *because* nothing wires them in sequence |
| orchestrator-workers | N `worker` spans, N decided at runtime | that N came from the model, and each worker span has an isolated input |
| evaluator-optimizer | `generate`/`evaluate` spans repeating K times | that K is the loop count and the exit was PASS vs. `max_iterations` |
| react-agent | alternating `agent` / `tools` spans until a final `agent` span | the turn count and which turn stopped calling tools |
| human-in-the-loop | two separate root spans (pause, then resume) sharing a thread | that the gap between them is a real `interrupt()` a human filled |

### Sending it somewhere real

The console exporter is only the default. Point OpenLLMetry at any
OTLP-compatible backend — [Arize
Phoenix](https://github.com/Arize-ai/phoenix) and
[Langfuse](https://langfuse.com/) both run locally and both ingest OTLP —
by exporting the standard variables and `ADP_OTEL_OTLP=1`:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:6006/v1/traces  # Phoenix
export ADP_OTEL_OTLP=1
uv run main.py run react-agent --otel
```

## Which one do I want?

- **Learning the pattern** → the narrated trace. That is what this repo is for.
- **Seeing what production sees** — token cost, latency per step, prompt
  payloads, a tree you can ship to a backend → `--otel`.
- **Comparing frameworks** on a vendor-neutral axis → `--otel`, and see
  [`ai-harnesses`](https://jithinkk.github.io/ai-harnesses/), where the
  span tree is the common denominator across five runtimes.
