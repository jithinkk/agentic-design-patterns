# Parallelization (Sectioning)

Splits one input into several **independent** subtasks — here, sentiment,
one-sentence summary, and keyword extraction over the same text — that run
concurrently because none of them depends on another's output, then joins
the results in an aggregation step.

**Use it when** a task cleanly decomposes into independent aspects that can
be evaluated separately and combined afterward. (The other flavor of this
pattern, "voting" — running the same prompt N times and combining the
results for a confidence check — uses the same fan-out/fan-in shape.)

## Graph shape

```
        ,--> sentiment --.
START --+--> summary ----+--> aggregate -> END
        '--> keywords ---'
```

LangGraph runs all three branches in the same superstep and only starts
`aggregate` once all three have produced output — no extra coordination
code required.

## Run it

```bash
python main.py run parallelization "The new release is great, though onboarding docs need work."
```

## Test it

```bash
pytest patterns/parallelization -v
```
