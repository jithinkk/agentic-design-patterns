"""Opt-in OpenTelemetry tracing for the pattern runs (`--otel`).

Off by default and **not** a runtime dependency of the patterns. The
narrated trace `main.py` prints (see each pattern's `run.py::render`) is
the primary "what shape is this?" view and needs nothing installed.

`--otel` is the second view: the same run, seen the way production sees it
-- a span tree on the OpenTelemetry GenAI semantic conventions. Turn it on
with::

    uv sync --group otel
    uv run main.py run orchestrator-workers --otel

That pulls in Traceloop's OpenLLMetry SDK, which auto-instruments
LangChain / LangGraph and the Anthropic / OpenAI clients. This helper
wires the resulting spans to a console exporter so the tree prints to your
terminal with no backend and no API key. To send it somewhere real
instead (Jaeger, Arize Phoenix, Langfuse, Grafana Tempo, ...), set the
standard ``OTEL_EXPORTER_OTLP_ENDPOINT`` env var and drop the
``--otel``-implied console exporter by exporting ``ADP_OTEL_OTLP=1``.

See docs/observability.md for how the span tree lines up with each
pattern's mechanic.
"""

from __future__ import annotations

import os

_INITED = False


def enable_console_otel() -> None:
    """Initialise OpenLLMetry with a console span exporter. Idempotent."""
    global _INITED
    if _INITED:
        return

    try:
        from traceloop.sdk import Traceloop
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised via CLI
        raise SystemExit(
            "--otel needs the optional 'otel' dependency group:\n"
            "    uv sync --group otel\n"
            "or, with pip:  pip install 'agentic-design-patterns[otel]'"
        ) from exc

    # OpenLLMetry phones home anonymous usage stats by default; a teaching
    # repo has no reason to. Set before init so it takes effect.
    os.environ.setdefault("TRACELOOP_TELEMETRY", "false")

    if os.getenv("ADP_OTEL_OTLP") == "1":
        # Respect a real OTLP endpoint from the environment instead of the
        # console. Traceloop reads OTEL_EXPORTER_OTLP_ENDPOINT itself.
        Traceloop.init(app_name="agentic-design-patterns", disable_batch=True, telemetry_enabled=False)
    else:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        Traceloop.init(
            app_name="agentic-design-patterns",
            exporter=ConsoleSpanExporter(),
            disable_batch=True,
            telemetry_enabled=False,
        )

    _INITED = True
