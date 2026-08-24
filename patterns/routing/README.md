# Routing

A cheap classification step inspects the input and dispatches it to one of
several specialized downstream prompts (in a real system, potentially
different models, tools, or context per branch), instead of forcing one
generic prompt to handle every kind of request well.

**Use it when** inputs fall into distinct categories that are each better
served by a focused prompt (or a different model/tool) than by one
one-size-fits-all prompt.

## Graph shape

```
START -> classify --billing--> billing_handler   -> END
              |----technical--> technical_handler -> END
              '----general----> general_handler   -> END
```

## Run it

```bash
python main.py run routing "I was charged twice for my subscription"
```

## Test it

```bash
pytest patterns/routing -v
```
