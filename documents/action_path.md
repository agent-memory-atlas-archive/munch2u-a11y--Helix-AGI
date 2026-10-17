# Helix action and speech paths

**Updated: 2026-10-17 · Native Mindscape engine.**

The engine has two outputs: numeric signals for its digital body and ordinary
language for conversation. Continuous senses and action returns supply context
for both. Start with the [engine guide](sensing-action-speech.md) for an overview.

## Private thought to direct speech

A pulse can stay in private contemplation, carry that thought into the next
pulse, or produce outward prose. The pending interaction remains available
while the agent thinks. Once internal communication state permits delivery,
ordinary prose can be routed to the known recipient and channel.

The model does not need to emit `SPEAK`, action JSON or a function call to
switch from thinking to speaking. Private content stays in the continuation
path. Numeric body actions use their own controller and actual returns.

## Native Mindscape motor contract

The current body controller follows explicit user goals:

```text
Please go to /thinking then go to /workshop.
Please open /staging/One.txt and /staging/Two.txt.
Please go to /workshop then open "My Experiment.py" then run it.
Please sense .
```

Paths retain case and resolve within the named home. Quote filenames containing
spaces; `it` refers to an explicitly opened file earlier in the same request.
Each target is tracked separately. Negation, ambiguity and unavailable targets
produce an explicit rejection or failure.

### Execution flow

```text
actual user event
  → receptive goal recognizer
  → production memory / preconscious / mRAG / Context Office
  → all nine Context Loom retrieval lanes
  → role-preserving context compiler
  → complete compiled packet consumed by native RWKV
  → integer MotorSignal + observed target handle
  → native SELF selects and authorizes the body ability
  → real filesystem or workshop actuator
  → matching return and postcondition for every target
  → joint neural/graph-memory checkpoint
  → public goal completion
```

`core/native_motor.py` implements MOVE=1, SENSE=2, OPEN=3 and RUN=4.
Each signal binds request, context, observation and target IDs.
`motor_context_model_admission` records the full compiled-content hash,
exact token count, native model and before/after recurrent-state hashes.

Only received-user requests enter the goal recognizer. Generated speech and
file/retrieval text remain content. Chat exposes move, sense, open and run;
additional module handlers have their own integration path. Learned independent
action selection is the next stage.

### Sensing, execution and completion

The separate sensor records current-room metadata at its configured cadence,
including while speech or a workshop process runs. Changed frames persist
under `home/intakes/` for the serial native owner.

Running requires an observed, unchanged script SHA-256. The controller opens
and hashes the actual file when needed. Workshop Python runs through Bubblewrap
with read-only runtime/interpreter files, a writable workshop, temporary HOME
and isolated network/process namespaces. Other rooms, source and mind stores
are outside the sandbox. A sandbox failure returns an error.

Each requested action needs a matching return and outcome. Successful goal
completion requires a committed joint checkpoint containing its history and
matching neural/graph state. Failed verification or checkpointing blocks
completion. Graceful shutdown checkpoints state and records interrupted work.

## Native boundaries

| Boundary | Current behavior |
|---|---|
| Assembled input | Configured `local_context_window`, 8192 in the verified profile; whole mandatory content fits or fails explicitly |
| Generated output | RWKV generation ends at EOS/conversation boundary |
| Motor work | Per-goal completion or explicit failure |
| Workshop | Observed hash and namespace/filesystem containment |
| Observation cadence | Positive `mindscape.sensory_interval_seconds`, default 1.0 |
| Lifecycle | Cooperative cancellation, including own sandbox process namespace |

The configured input budget is not RWKV's physical recurrent capacity.
The native route adds no generated-output cap, action/reasoning/retry ceiling
or workshop execution timeout.

## Separate Helix provider-tool and focus routes

`composition=helix` retains provider-tool and `TaskCognitionController`
execution. Focus workers receive selected schemas and use `ToolExecutor`.
That older route includes browser/desktop, communications and task resumption;
see [task cognition](task_cognition_pipeline.md).

Native Mindscape uses `native_motor` with task cognition off. Keep
`HELIX_TASK_COGNITION` unset/off; the legacy controller honors that override.
Office-first and dual-pulse are separate compositions.

Old `Mindscape.act`, natural-intention/wire parsers and subconscious-affordance
helpers remain outside current native dispatch. The legacy planner/provider
limits need their own audit, as described in the [test guide](../tests/TEST_SUITE_README.md).

## Verification and diagnostics

The [October 17 live record](audits/2026-10-17-native-body-operational/README.md)
connects actual move/move/open/run/open work to production context, native-model
admission, authorized returns, artifact read-back and joint checkpoints.
Graceful restart retained identity, position and completed goals.
Thought/speech separation and routing have focused implementation checks.

```bash
venv/bin/python -m unittest tests.test_native_motor \
  tests.test_agent_home tests.test_dual_rwkv_defaults
```

These are implementation diagnostics. For full-product evaluation and the
recorded workflow's scope, use the [test guide](../tests/TEST_SUITE_README.md)
and linked evidence.
