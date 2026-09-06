"""Tiny formatting helpers shared by every pattern's `run.py::render`.

`render` turns a finished run's state dict into a short, plain-text trace
that narrates the pattern's *mechanic* -- how many LLM calls, in what
shape, which branch was taken, how many loop turns -- rather than dumping
the raw state (that's still one `--raw` away). Keeping the header and the
"one step per line" idiom in one place is what lets you diff two patterns'
traces and see the structural difference at a glance.
"""

from __future__ import annotations

RULE = "─" * 60


def header(name: str, shape: str) -> str:
    """The first two lines of every trace: `name · shape`, then a rule."""
    return f"{name} · {shape}\n{RULE}"


def block(label: str, body: str) -> str:
    """A labelled multi-line payload (the final report, the response, ...)."""
    body = (body or "").rstrip("\n")
    return f"\n{label}:\n{body}"


def step(text: str, *, indent: int = 2, bullet: str = "") -> str:
    """One line of the trace, optionally bulleted and nested."""
    pad = " " * indent
    return f"{pad}{bullet + ' ' if bullet else ''}{text}"


def truncate(text: str, limit: int = 88) -> str:
    """Collapse whitespace and clip, for inline previews of a step's output."""
    flat = " ".join((text or "").split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"
