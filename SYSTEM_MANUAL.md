# Helix System Manual

**Source review: 2026-10-17 · Scope: current `mindscape` composition.**
This is an operator/developer reference, not an agent system prompt.
See [architecture](documents/architecture_current.md) for wiring and
[launch](documents/mindscape_launch.md) for complete creation commands.

## Select and start an agent

The graphical wizard (`./install.sh`) provisions identity, named home,
persistent stores, archetype seed and channel configuration. The CLI currently
requires an explicit creation-manifest provisioning step; follow the
[command-line creation instructions](documents/mindscape_launch.md#command-line-creation).

```bash
venv/bin/python main.py
venv/bin/python dashboard/dashboard.py --port 5050
```

Run these in separate terminals from the Helix root. The main process uses
`config/config.json`'s selected `data_dir`; `--data-dir` overrides it without
creating a matching home or identity. The GUI launcher can start the dashboard.
Plain `main.py` does not start the HTTP server.

`venv/bin/python main.py --check-setup` loads and synchronizes actual state and
can create checkpoints. It exits before continuous channel/body operation;
successful initialization does not establish conversational or action ability.

## Identity, home and communication

Guided creation normally uses `data/homes/<Agent Name>` for the filesystem
body and `data/agents/<Agent Name>` for canonical memory/native state. The name
can contain spaces or Unicode but not path separators/control characters.
Established native identity and archetype must match the creation contract;
changing setup fields cannot rewrite an existing gestation.

| Choice | Meaning |
|---|---|
| Generalist / `balanced` | Native balanced preference seed |
| Explorer / `curious` | Native preference for inspection and discovery |
| Careful analyst / `deliberate` | Native preference for evidence checking |
| Builder / `builder` | Native preference for practical construction |
| Basic / standard / predeveloped | Starter belief/memory depth |
| Voice wording | Bootstrap text style, separate from the native archetype |

These are initial preferences and text seeds, not trained competencies.
The optional nursery helper is not called during normal creation or startup.

Dashboard needs no channel token. The wizard also handles Telegram and Discord;
the CLI includes Slack, WhatsApp and webhook options. External channels require
explicit enablement and their own credentials. Credentials belong in
`~/.config/helix/credentials.env`, outside the repository and creation manifests.
A selected primary channel does not prove a service connection or delivered reply.

The home contains `thinking`, `modules`, `bedroom/closet`, `workshop` and
`intakes`. Dashboard uploads create/use `staging`. On first attachment the
body starts in the thinking room; graceful restart preserves position.
See [agent home](documents/agent-home.md) for containment and module contracts.

## Request and inspect actions

Use Dashboard Chat, then **Environment and actions** to inspect the actual
body result independently of a language response.

```text
Please go to /workshop then open Example.py then run it.
Please open /staging/FirstNote.txt and /staging/SecondNote.txt.
Please sense .
```

The current receptor accepts explicit move/sense/open/run commands. Quote
filenames with spaces; case is preserved. `it` binds only to an explicitly
opened file earlier in the same request. Each requested target is tracked.
Ambiguous, negated or failed requests cannot be completed by guessing.

This is a bootstrap command policy. It does not yet expose arbitrary file
creation, web/module activation or sleep through native Chat. Related handlers
exist in the body, but a registered handler alone is not a connected action
route. Model speech and retrieved/file text have no execution authority.

Before execution, the real user request traverses persistent retrieval,
all nine Loom lanes, context compilation and actual native RWKV consumption.
Integer motor signals identify observed targets; native SELF must authorize
the corresponding one-use body ability. The goal completes publicly only
after matching returns for every obligation and a joint checkpoint.

Python files must be inside the workshop and have an observed matching SHA-256.
The sandbox mounts only the workshop writable, system/interpreter/runtime
files read-only, and temporary namespace files. Network and process namespaces
are isolated. Other rooms, source and mind state are not mounted. Execution
fails explicitly if Bubblewrap is unavailable; there is no host fallback.

## Observe health and state

| Surface | What it reports |
|---|---|
| Dashboard Chat | User messages and routed language replies |
| Environment and actions / `GET /api/motor` | Actual goal state, file contents, stdout, errors and foreground health |
| File staging / `/api/stage_file` | Uploads to the configured named home's staging folder |
| `mindscape/receipts.jsonl` | Context/model admission, actions, observations and checkpoints |
| `mindscape/foreground-health.json` | Explicit language success/failure state |
| `home/intakes/` | Changed current-room filesystem observations |

A language failure can park the foreground while the independent body remains
receptive. Absence of a spoken reply is not an action failure or success receipt.
Inspect the body outcome and artifact, not the model's claim about it.

Some older dashboard location and Module Studio code still assumes
`data_dir/agent_home`; it is not the authoritative named-home view. AST parsing
in Module Studio checks syntax only and does not install a native capability
or prove containment. The supported trial path used Chat, staging and the
Environment and actions panel.

## Configuration and boundaries

Configuration is in `config/config.json`; provider/channel environment values
also exist in the private credentials file. Mindscape validates the composition
before importing the native dependency.

| Key | Meaning |
|---|---|
| `composition` | `mindscape` for this integrated native route; `helix` selects separate legacy paths |
| `pulse_mode` | `standard` required by Mindscape; legacy dual-pulse is a different composition |
| `local_provider`, `llm_provider` | `rwkv` for the default native profile; optional Ollama foreground is separately configured |
| `local_model`, `llm_model` | Actual foreground checkpoint or selected local model |
| `local_context_window` | Assembled-input token budget; 8192 in the verified profile, not RWKV's physical recurrent capacity |
| `data_dir` | Selected agent's persistent state |
| `mindscape.package_path` | Declared MightyMem source with compatible gestation and lifecycle interfaces |
| `mindscape.rwkv_model` | Pinned native model directory |
| `mindscape.home` | Actual body root; distinct from source, weights and mind state |
| `mindscape.device` | `cpu`; current joint bridge rejects other devices |
| `mindscape.gestation` | `if_missing` or `resume_only` |
| `mindscape.action_intent_source` | Normalized to `native_motor`; old speech-action aliases migrate |
| `mindscape.sensory_interval_seconds` | Positive observation cadence; default 1.0 |
| `mindscape.context_focus_profiles` | Positive role-admission preferences for current activities |
| `mindscape.modules_require_room` | Default false for installed module handler; does not add a Chat activation opcode |
| `task_cognition_mode` | Off in the supported native profile; keep `HELIX_TASK_COGNITION` unset/off |
| `active_hours` | Wake/sleep schedule; the recorded trial used equal start/end for continuous wakefulness |

The native RWKV route has no output-token cap, action-count cap or workshop
execution timeout. EOS/conversation boundaries finish language generation.
Mandatory input-budget overflow fails explicitly; contributions are not silently
clipped. Other provider and experimental routes have inherited limits that
need separate audit before evaluation.

## Runtime rhythm and sensory intake

| Pulse state | Default cadence | Transition |
|---|---:|---|
| ACTIVE | 10 seconds | Incoming user/critical activity wakes the loop |
| REGULAR | 30 seconds | After two minutes without incoming activity |
| RESTING | Configurable, normally 15 minutes | After ten minutes in REGULAR |
| DORMANT | Scheduled sleep window | Background dream/consolidation route |

The language pulse drains events, prepares retrieval/context, generates private
thought/speech, stores canonical records, advances physics and runs post-pulse
hooks. Native actions are scheduled independently; legacy intention-to-task
inception is disabled in this composition.

The filesystem sensor has its own cadence. It samples current-room metadata
without opening contents, persists changed frames and records each tick.
Unchanged frames are deduplicated for neural admission. Sensing continues while
speech or a sandbox process runs; the serial native owner admits queued frames
when available.

## Memory and context reference

Canonical belief stores contain seven categories: `premises`,
`propositions`, `preferences`, `people`, `skills`, `desires` and
`concepts`. Confidence, mass, stability, provenance and affective metadata
influence storage/retrieval. A belief labeled as a skill is not by itself
evidence of successfully executed work.

The journal stores exact events, thoughts and action-related records.
Typed `RecordEnvelope` views distinguish inbound/outbound messages, private
thought, tool/action results and evidence status. Historical assistant claims
do not become verified observations on recall.

Helix mRAG uses normalized 1024D Qwen3 semantic vectors, exact terms and
multi-head queries. Context Office builds source-linked evidence briefs.
Separate 8D belief/memory fields and directed transition associations supply
lateral context; their scores do not rerank semantic evidence. Maintained
Markdown views preserve canonical IDs rather than forming an independent
truth store.

Context Loom enables semantic, exact, recent, subjective, procedure, correction,
multi-hop graph, Y-cipher depth and Habitus graph lanes. The final compiler
preserves those roles and complete source contributions, recording admission
and exclusion decisions. Activity priorities are bootstrap settings rather
than learned neural attention.

Affect and stability are runtime signals for attention/posture, not truth,
permission or proof of subjective experience. The older manual's standalone
`core/somatic_engine.py` and `tools/internal_sleep_tool.py` references do not
exist in this checkout and are not installed features.

## Auxiliary work, sleep and learning

Belief detection, summarization and Curator consolidation can invoke the
configured language provider. They are not all inference-free CPU hooks.
The native profile uses the selected local provider for auxiliaries; configured
local failure cannot silently route batch work to Gemini.

The production `BackgroundDaemon`/Curator handles scheduled dream work.
The bedroom's sleep descriptor points at that attached engine; this differs
from the nursery's separate simulated sleep helper. Native Chat has no sleep
opcode. A cycle receipt alone does not establish sound belief formation,
source provenance or later recall.

RWKV gradient training is disabled in this adapter. Recurrent state, graph
activity, belief maintenance and procedural records are distinct mechanisms;
none should be reported as learned neural motor competence without evidence.
The native body's bridge into Helix's legacy procedural learner is still
pending. See [nursery status](documents/nursery_status.md) before using its helper.

## Shutdown, restore and verification

Use Ctrl-C or SIGTERM for cooperative cancellation and a joint shutdown
checkpoint. Active native compute observes explicit cancellation at chunk
boundaries; foreground/auxiliary sessions cancel and the runtime can interrupt
its own sandbox process namespace. Preserve the external MightyMem cancellation
change when reproducing this lifecycle.

Back up the selected home, canonical agent data and native checkpoint lineage
together. Graceful restart has retained identity, room and completed motor
goal history in the recorded trial. Crash-atomic replay of all intermediate
actions and exactly-once projection activation remain unestablished.

The [October 17 operational record](documents/audits/2026-10-17-native-body-operational/README.md)
documents real movement, file opening, isolated Python execution and restart.
The recorded 72 focused checks are implementation diagnostics, not a product
score. General conversational coherence, factual recall accuracy, learned
autonomy and growth remain unverified. The
[test guide](tests/TEST_SUITE_README.md) defines the evidence required for a new
full-system result.
