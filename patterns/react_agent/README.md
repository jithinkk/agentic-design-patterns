# ReAct Agent (Reason + Act)

The canonical "agent" loop: the model gets a system prompt, the tools it's
allowed to use, and the conversation so far; it either emits a tool call
or a final answer. Tool calls run through LangGraph's prebuilt `ToolNode`
and the result loops back to the model as a `ToolMessage`, repeating until
the model answers without calling a tool.

**Use it when** the number of steps can't be predicted up front and the
model itself needs to decide, turn by turn, whether it has enough
information to answer or needs to act first. This is the most open-ended
(and hardest to fully predict) pattern here — the other five are better
described as fixed "workflows."

## Graph shape

```
START -> agent --tool_calls present--> tools --> agent (loop)
            '-------no tool calls-----------> END
```

Built from `langgraph.prebuilt.ToolNode` and `tools_condition` directly
against a `StateGraph`, rather than the one-line `create_react_agent`
helper, so the loop is visible end to end.

## Run it

```bash
python main.py run react-agent "What is (12 + 8) * 3?"
python main.py run react-agent "Explain what langgraph is used for"
python main.py run react-agent "What is the capital of France?"
```

## Test it

```bash
pytest patterns/react_agent -v
```
