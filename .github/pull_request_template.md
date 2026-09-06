## Summary

<!-- What changed, and why. A few bullets is usually enough. -->

-

## Test plan

<!-- How you verified this. Check what applies, delete what doesn't. -->

- [ ] `uv run pytest -v` passes — every pattern, all offline
- [ ] `uv run mkdocs build --strict` is clean
- [ ] `uv sync --locked` succeeds (no lockfile drift)

## If this adds a new pattern

<!-- Delete this section if it doesn't apply. See README's "Adding a new pattern". -->

- [ ] `nodes.py`: node functions plus a `_fake_responder` giving
      deterministic behavior for tests, wired up via
      `get_chat_model(responder=_fake_responder)` — runs fully offline, no
      API key.
- [ ] `graph.py`: a `TypedDict` state and a `build_graph()` wiring nodes
      with `add_edge`/`add_conditional_edges`.
- [ ] `run.py`: a `main(...)` function and a CLI-runnable
      `if __name__ == "__main__"` block.
- [ ] Tests in `tests/test_<name>.py`; pattern registered in `main.py`'s
      `PATTERNS` dict.
- [ ] Docs: a `docs/patterns/<name>.md` page, an `mkdocs.yml` nav entry, and
      (if relevant) a row in `docs/architecture-overview.md`'s comparison
      table.
