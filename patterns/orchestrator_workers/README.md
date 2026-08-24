# Orchestrator-Workers

Like `parallelization`, but the number and shape of the parallel subtasks
**isn't known ahead of time** — an orchestrator LLM call decides that at
runtime. LangGraph's `Send` primitive lets a routing function fan out to a
worker node once per subtask it just invented, and their results
accumulate into a single list via a reducer before a synthesizer combines
them.

**Use it when** the subtask breakdown is genuinely dynamic — code review
across an unknown number of changed files, research across a
model-chosen set of subtopics, etc. If you can enumerate the subtasks in
advance, plain `parallelization` is simpler.

## Graph shape

```
START -> orchestrator --Send(worker, subtask)×N--> worker -> synthesizer -> END
```

`orchestrator` writes `subtasks: list[str]`; the routing function
`continue_to_workers` turns that into `N` `Send("worker", {"subtask": ...})`
calls; each `worker` run appends one `{"subtask", "result"}` entry to
`worker_results` (an `Annotated[list, operator.add]` reducer) so the
partial results from all the parallel runs land together for
`synthesizer`.

## Run it

```bash
python main.py run orchestrator-workers "Write a report covering pricing, onboarding, and support quality."
```

## Test it

```bash
pytest patterns/orchestrator_workers -v
```
