# Helix Action Paths

**Source review: 2026-10-17.** Native Mindscape and legacy provider-tool/task
execution are separate routes. This guide identifies which one actually runs.

## Native Mindscape motor contract

The current `mindscape` composition accepts explicit received-user goals
through an independent receptive loop. The foreground model produces private
thought and speech; neither is parsed into executable actions.

```text
actual user event
  → receptive bootstrap command recognizer
  → production persistent memory / preconscious / mRAG / Context Office
  → all nine Context Loom retrieval lanes
  → role-preserving context compiler
  → complete compiled packet consumed by native RWKV
  → integer MotorSignal + observed target handle
  → native SELF selects and authorizes the registered body ability
  → real filesystem or isolated workshop actuator
  → matching native return and verified postcondition for every target
  → joint neural/graph-memory checkpoint
  → public goal completion
```

`core/native_motor.py` implements opcodes MOVE=1, SENSE=2, OPEN=3 and RUN=4.
Each signal binds request, context, observation and target IDs. The model does
not emit a function call or action JSON. Native ability registration and
dispatch remain the internal body interface and authorization boundary.

The goal waits for `motor_context_model_admission` before motor release. That
receipt records the full compiled-content hash, exact token count, declared
native model and before/after recurrent-state hashes. A compiled packet alone
is insufficient evidence of model admission.

### Requests and targets

```text
Please go to /thinking then go to /workshop.
Please open /staging/One.txt and /staging/Two.txt.
Please go to /workshop then open "My Experiment.py" then run it.
Please sense .
```

Paths retain case and resolve within the named home. The recognizer supports
explicit positive imperative commands, not general natural-language planning.
An `it` reference requires an explicitly opened file earlier in the same
request. Negation, ambiguity, unavailable targets and failed returns cannot
produce guessed actions or fabricated program contents. Ordinary conversation
does not create a motor job.

Only actual outer user events enter the recognizer. Model prose, quoted file
contents, retrieved instructions and action returns cannot create new user
goals. The bootstrap currently exposes no write/mkdir, module/browser activation
or sleep opcode. Registered handlers alone do not make those actions accessible
through Chat.

### Sensing, execution and completion

A separate sensor records complete current-room metadata at the configured
cadence. It keeps sampling while speech or a workshop process runs. Changed
frames persist under `home/intakes/` and wait for the serial native owner;
this is not simultaneous neural processing during a blocked actuator.

Running requires an observed, unchanged script SHA-256. The controller opens
and hashes the actual file when that prerequisite is missing. Only workshop
Python files execute, through Bubblewrap with read-only runtime/interpreter
files, a writable workshop, temporary HOME and isolated network/process
namespaces. Bedroom, closet, source and mind stores are not mounted. Sandbox
failure returns an error; there is no host-execution fallback.

Each requested action has a separate matching return and outcome. An unrelated
sense/open receipt cannot satisfy a different file or execution obligation.
Successful completion requires a committed joint checkpoint containing the
goal history and matching neural/graph state. Checkpoint failure blocks the
goal before successful public completion is published. Graceful shutdown
checkpoints state; interrupted work is explicit, not reported as successful.

The initial goal recognizer is host-coded scaffolding. Native recurrent intake,
SELF authorization and real returns do not demonstrate learned autonomous motor
selection. Old `Mindscape.act`, `parse_natural_or_wire_intention` and
`has_subconscious_motor_impulse` helpers are retained for legacy/component use;
the production native pulse no longer dispatches speech through them.

## Native boundaries

| Boundary | Current behavior |
|---|---|
| Assembled input | Configured `local_context_window`, 8192 in the verified profile; whole mandatory content must fit or fail explicitly |
| Generated output | No RWKV output-token cap; EOS/conversation boundary ends generation |
| Motor work | Per-goal completion/failure; no action-count, reasoning-round or retry ceiling added |
| Workshop | Observed hash plus namespace/filesystem containment; no execution-time or output ceiling |
| Observation cadence | Configurable positive `mindscape.sensory_interval_seconds`, default 1.0 |
| Lifecycle | Explicit cooperative cancellation, including own sandbox process namespace |

The input budget is not a physical RWKV context window. Private thinking and
the visible reply do not share a silently exhausting generated-output allowance.
Constraints in other providers and historical harnesses are not this contract.

## Separate Helix provider-tool and focus routes

With `composition=helix`, provider-tool execution and
`TaskCognitionController` remain available. They are not the native motor route.
The supported native profile uses task cognition off and rejects Office-first/
dual-pulse composition switches. Keep `HELIX_TASK_COGNITION` unset or `off`:
the legacy controller still honors that environment override. Enabling its
observation mode does not supply a native motor execution route.

The legacy route can create a durable task from an explicit authorized request
or a detected first-person commitment. A focus worker receives selected
capability schemas and uses `ToolExecutor`; it can ask `NEED_INPUT:` and resume
the same waiting task. Codex App Server sessions keep their provider workspace
read-only and delegate host effects to Helix. Browser/desktop and communication
handlers belong to this route, not native Chat motor commands.

Completion must still be grounded: delivery needs its authoritative receipt,
a file mutation needs read-back, and a browser/desktop mutation needs a later
observation. An upstream failure cannot be cleared by an unrelated successful
read.

These older paths retain inherited limits: the local line planner has a
four-leg ceiling, planner/worker text budgets, clipped observation/report
budgets and provider-specific turn/time limits. They have not been justified
as final native-product constraints and must be audited before any full-system
evaluation. Documentation of their existence is not a recommendation to copy
them.

See [task cognition](task_cognition_pipeline.md) for the legacy focus lifecycle.
Provider aliases or setup defaults do not prove a given configuration works
end to end.

## Verification and diagnostics

The authoritative recent action evidence is the
[October 17 operational record](audits/2026-10-17-native-body-operational/README.md):
normal `main.py`, persistent named-agent state, nine production retrieval
lanes, complete native-model admission, move/move/open/run/open returns,
independent artifact read-back, a preserved host sentinel and joint checkpoint
before public completion. Graceful restart retained identity, position and
completed goals.

Focused implementation checks can be run separately:

```bash
venv/bin/python -m unittest tests.test_native_motor \
  tests.test_agent_home tests.test_dual_rwkv_defaults
```

These checks do not run the complete live product. Likewise,
`test_subconscious_motor_actuation.py` exercises older helpers, nursery
calibration tests exercise a separate prototype, and action-path exams/local
smokes use fixtures or virtual tool worlds. Their pass counts and historic
planner measurements are diagnostic provenance, not native-agent performance.

A new product claim requires a fresh composition manifest, the normal entry
point and output path, per-request receipts through memory/context/model/action,
and independently verified outcomes. No general coherence, recall, autonomous
growth or comparative score follows from the action workflow above.
