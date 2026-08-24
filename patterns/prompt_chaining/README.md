# Prompt Chaining

Decomposes a task into a fixed sequence of LLM calls, where each step's
output feeds the next. A plain Python **gate** sits between the first two
steps and can stop the chain before the (usually more expensive) later
steps run — cheaper and more reliable than trusting one LLM call to do
everything correctly in one shot.

**Use it when** a task decomposes into clear sequential steps and each step
is easier for the model to get right on its own than a single combined
prompt would be.

## Graph shape

```
START -> generate_outline -> gate_check --continue--> expand_draft -> polish -> END
                                    \--stop--> END
```

`gate_check` is not an LLM call — it's a programmatic check on the
outline's shape.

## Run it

```bash
python main.py run prompt-chaining "Why LangGraph is useful for agents"
# or directly:
python -m patterns.prompt_chaining.run "Why LangGraph is useful for agents"
```

## Test it

```bash
pytest patterns/prompt_chaining -v
```
