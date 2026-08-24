# Evaluator-Optimizer

One LLM call generates a solution; a second, separate call grades it
against explicit criteria and returns pass/fail plus feedback. On failure,
the feedback is folded back into the next generation attempt, and the loop
repeats until it passes or a `max_iterations` cap is hit.

**Use it when** there are clear evaluation criteria and iterative
refinement measurably improves the result — similar to how a human writer
revises against an editor's notes.

## Graph shape

```
START -> generate -> evaluate --accept--> END
              ^            |
              '---revise---'
                            '--give_up--> END  (iteration >= max_iterations)
```

## Run it

```bash
python main.py run evaluator-optimizer "Write a tagline for Nimbus"
```

## Test it

```bash
pytest patterns/evaluator_optimizer -v
```
