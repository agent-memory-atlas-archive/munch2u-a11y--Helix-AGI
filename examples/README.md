# Helix AGI Developer Examples

**Reviewed: 2026-10-17 · Scope: isolated API demonstrations.**

These examples construct individual subsystems or legacy action routes. They
do not launch the current native Mindscape product or establish its competence.
For production startup use [the launch guide](../documents/mindscape_launch.md);
for numeric body commands use [the action contract](../documents/action_path.md).

Example 03 retains a four-leg planner ceiling from the legacy implementation.
It is not a native motor limit or a recommended final-system constraint.

## Available Examples

| Example Script | Description |
|---|---|
| [`01_basic_pulse_loop.py`](01_basic_pulse_loop.py) | Demonstrates setting up `PulseLoop`, event queueing (`emit`), and observing pulse state transitions. |
| [`02_custom_tool_registration.py`](02_custom_tool_registration.py) | Shows how to declare custom Python tool handlers with `ToolRegistry` and execute them via `ToolExecutor`. |
| [`03_action_path_planning.py`](03_action_path_planning.py) | Demonstrates the legacy `ActionPlanner`, its inherited 4-leg ceiling, clarification handling (`NEED_INPUT:`), and verification receipts. |
| [`04_typed_memory_retrieval.py`](04_typed_memory_retrieval.py) | Demonstrates querying `UnifiedRetrieval` and inspecting typed evidence assertions decorated by `RecordEnvelope`. |

## Running Examples

Execute any example script using the project virtual environment:

```bash
venv/bin/python examples/01_basic_pulse_loop.py
venv/bin/python examples/02_custom_tool_registration.py
venv/bin/python examples/03_action_path_planning.py
venv/bin/python examples/04_typed_memory_retrieval.py
```
