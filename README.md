# 🤖 Agentic Design Patterns - Exploratory Sandbox

A comprehensive exploration and implementation of agentic AI design patterns using **LangGraph**, **LangChain**, and modern LLM frameworks. This sandbox provides hands-on implementations of cutting-edge autonomous agent architectures.

## 📋 Overview

This project is a **research and experimentation platform** for understanding how to build sophisticated autonomous agents. It includes multiple design patterns, each demonstrating different approaches to agent reasoning, planning, and execution.

### Key Capabilities
- **Multi-pattern architecture**: Compare and contrast different agentic approaches
- **LangGraph-based workflows**: Production-ready graph-based state management
- **Tool integration**: Seamless execution of custom tools and external APIs
- **Memory systems**: Context management and conversation history
- **Guardrails**: Safety constraints and output validation
- **Multi-LLM support**: OpenAI, Hugging Face, and more

## 🏗️ Architecture

```
agentic-design-patterns/
├── patterns/                      # Core agentic pattern implementations
│   ├── langgraph_react/          # ReAct pattern with LangGraph
│   ├── planner_executor/         # Planner-executor pattern
│   └── react_agent/              # React agent implementation
├── shared/                        # Shared utilities and infrastructure
│   ├── guardrails/               # Safety constraints and validators
│   ├── llm/                       # LLM integrations (OpenAI, HF, etc.)
│   ├── memory/                   # Memory and context management
│   └── tools/                    # Tool definitions and executors
├── notebooks/                     # Jupyter exploratory notebooks
├── experiments/                   # Experimental implementations
└── main.py                        # Entry point
```

## 📦 Design Patterns Included

### 1. **LangGraph ReAct** (`patterns/langgraph_react/`)
ReAct (Reasoning + Acting) pattern using LangGraph's graph-based state management.
- **What it does**: Iteratively reasons about tasks and takes actions
- **Best for**: Complex multi-step reasoning, tool-heavy workflows
- **Key files**: `graph.py`, `nodes.py`, `run.py`

### 2. **Planner-Executor** (`patterns/planner_executor/`)
Separates planning from execution for more structured task completion.
- **What it does**: First plans actions, then executes them sequentially
- **Best for**: Deterministic workflows, task decomposition
- **Key files**: Task planning and execution modules

### 3. **React Agent** (`patterns/react_agent/`)
Standard ReAct agent pattern with flexible tool integration.
- **What it does**: Agent loops through reasoning and tool calls
- **Best for**: General-purpose autonomous tasks

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- `uv` package manager (recommended) or `pip`
- API keys for LLM providers (OpenAI, etc.)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd agentic-design-patterns

# Install dependencies using uv
uv sync

# Or using pip
pip install -e .
```

### Setup Environment

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=sk-your-key-here
HUGGINGFACE_API_KEY=hf_your-key-here
```

### Run Examples

```bash
# Run the main entry point
python main.py

# Run specific pattern
cd patterns/langgraph_react
python run.py

# Explore in Jupyter
jupyter notebook notebooks/
```

## 🔧 Project Structure Details

### `shared/` - Shared Infrastructure

- **`llm/`** - Language model integrations
  - `hf_llm.py` - Hugging Face model wrapper
  - Support for OpenAI, local models, etc.

- **`memory/`** - Context and conversation management
  - Session memory
  - Conversation history
  - Context windows

- **`tools/`** - Tool definitions and execution
  - Tool registry
  - Tool executors
  - Integration with external APIs

- **`guardrails/`** - Safety and validation
  - Output validators
  - Input sanitizers
  - Policy enforcement

### `patterns/` - Design Pattern Implementations

Each pattern is self-contained with:
- `graph.py` - Graph/workflow definition
- `nodes.py` - Node implementations (agent logic)
- `run.py` - Executable entry point for testing

### `notebooks/` - Exploratory Analysis

Interactive Jupyter notebooks for:
- Pattern comparison
- Behavior analysis
- Debugging and visualization
- Ad-hoc experimentation

## 📚 Usage Examples

### Running the LangGraph ReAct Pattern

```python
from patterns.langgraph_react.run import run_agent

result = run_agent(
    task="Find the capital of France and tell me about it",
    max_iterations=10
)
print(result)
```

### Building Your Own Pattern

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    tools_called: list

# Define your state graph
builder = StateGraph(State)
builder.add_node("reason", my_reasoning_node)
builder.add_node("act", my_action_node)

graph = builder.compile()
result = graph.invoke({"messages": [...]})
```

## 🧪 Development

### Running Tests

```bash
pytest tests/
pytest --cov=patterns --cov=shared
```

### Code Quality

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type checking
pyright
```

### Adding a New Pattern

1. Create a new directory in `patterns/`
2. Implement `graph.py` with your state graph
3. Implement `nodes.py` with your logic
4. Create `run.py` as an executable example
5. Add tests and documentation

## 📖 Key Concepts

### State Graph Pattern
All patterns use **LangGraph's StateGraph** for managing agent workflows:
- Defines a `State` TypedDict for data flow
- Adds nodes for different computation steps
- Connects nodes with edges
- Compiles into an executable graph

### Tool Integration
Tools are integrated through:
- Tool definitions (schema, description, function)
- Tool executors (safely run tools)
- Tool memory (track tool calls)
- Result integration (feed results back to agent)

### Agent Loop
Standard agentic loop:
1. **Observe** - Process current state and available information
2. **Reason** - Use LLM to decide next action
3. **Act** - Execute tools or generate output
4. **Update** - Incorporate results into state
5. **Repeat** - Until goal reached or max iterations exceeded

## 🔌 Integrations

### LLM Providers
- **OpenAI** - GPT-4, GPT-3.5
- **Hugging Face** - Local and API-based models
- **Other**: LLaMA, Mixtral, etc. via LangChain

### Tools & APIs
- Web search
- Code execution
- File operations
- Custom integrations

### Memory
- Conversation history
- Session context
- Long-term memory stores

## 📊 Performance & Best Practices

- **Minimize LLM calls**: Cache results, use embeddings
- **Token efficiency**: Summarize context, use few-shot examples
- **Tool reliability**: Validate tool outputs, implement retries
- **Safety first**: Use guardrails for high-stakes applications
- **Observability**: Log agent reasoning and actions

## 🐛 Troubleshooting

### Common Issues

**API key not found**
```bash
# Verify .env file exists and contains:
cat .env
# OPENAI_API_KEY=sk-...
```

**Import errors**
```bash
# Reinstall package in development mode
pip install -e .
```

**LangGraph version conflicts**
```bash
# Check dependencies
pip show langgraph
# Update if needed
pip install --upgrade langgraph
```

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Agent Design Patterns](https://www.promptengineering.org/)

## 🤝 Contributing

Contributions welcome! Areas for exploration:
- New agentic patterns (Tree of Thought, HyDE, etc.)
- Additional tool integrations
- Improved guardrails and safety
- Performance optimizations
- Documentation and examples

## 📝 License

[Add your license here]

## 🙋 Support

For issues, questions, or pattern suggestions, please open an issue or discussion.

---

**Happy exploring! 🚀**
