# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an educational codebase for learning **Google Agent Development Kit (ADK)**. It contains two learning modules demonstrating how to build AI agents with Gemini models via Vertex AI.

- **Part 1** (`adk_learning_tools.py` / `ADK_Learning_tools.ipynb`): Single agents, custom function tools, agent-as-tool delegation, conversational memory
- **Part 2** (`adk_learning_tool_multi_agents.py` / `ADK_Learning_tool_multi_agents.ipynb`): SequentialAgent, LoopAgent, ParallelAgent, and router patterns

## Running the Code

```bash
# Run as Python scripts
python adk_learning_tools.py
python adk_learning_tool_multi_agents.py

# Run as interactive notebooks
jupyter notebook ADK_Learning_tools.ipynb
jupyter notebook ADK_Learning_tool_multi_agents.ipynb
```

**Prerequisites**: Google Cloud project with Vertex AI enabled. Set these environment variables:
```
GOOGLE_CLOUD_PROJECT=<your-project-id>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

The notebooks were originally designed for Google Colab (use `google.colab.auth.authenticate_user()` for auth there).

## Architecture

All agents use `gemini-2.5-flash` via `google-adk`.

### Core Execution Pattern
```python
session_service = InMemorySessionService()
session = await session_service.create_session(app_name=..., user_id=..., session_id=...)
runner = Runner(agent=agent, app_name=..., session_service=session_service)
# All execution is async/await
response = await runner.run_async(user_id=..., session_id=..., new_message=...)
```

### Key Patterns

**Session memory**: The same `session_id` gives agents conversation continuity; a new session means the agent has no memory of prior turns.

**Custom tools**: Regular Python functions become agent tools — the function signature and docstring are what the LLM sees, so docstrings must be precise and complete.

**Agent-as-tool**: Wrap an agent with `AgentTool(agent=...)` to let a parent agent call it like a function.

**State passing between chained agents**: Use `output_key="var_name"` on sub-agents to write results into the shared `state` dict; reference them in downstream agent instructions as `{var_name}`.

**LoopAgent exit**: Provide an `exit_loop()` tool to the critic/checker agent so it can signal when refinement is complete.
