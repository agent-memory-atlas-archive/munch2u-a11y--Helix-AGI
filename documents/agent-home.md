# Agent home and body

**Source review: 2026-10-17.** The home is filesystem data separate from the
source checkout, model weights and persistent mind stores. Guided creation
uses `data/homes/<Agent Name>` and `data/agents/<Agent Name>`; spaces and
Unicode are allowed after name validation. The wizard provisions identity and
creation manifests. The CLI has a provisioning gap documented in the
[launch guide](mindscape_launch.md#command-line-creation).

```text
<Agent Name>/
  thinking/          initially empty, quiet room
  modules/           installed web_search.py, web_read.py, terminal.py
  bedroom/
    sleep.json       descriptor for the attached production dream engine
    closet/          personal files
  workshop/          Python experiments and their persistent artifacts
  staging/           dashboard uploads, created when used
  intakes/           controller-owned surroundings observations
  home.json          rooms, modules and containment manifest
  identity.json      creation and native gestation identity
```

The body starts in `thinking` on first attachment. Subsequent graceful
restarts preserve its room and completed goal history. Moving from an older
workspace does not import source files into the home.
`mindscape.workspace` remains a legacy field; body operations use
`mindscape.home`.

## Current sensory and action route

The independent sensor samples real current-room attributes and immediate
entries every `mindscape.sensory_interval_seconds` (default 1.0). It does not
open file contents. Changed text/JSON observations persist under `intakes/`
and queue for native LOOK/RWKV admission; every tick has a receipt, including
unchanged frames deduplicated for neural intake. Sampling continues during
language generation and workshop execution. The serial native owner processes
queued frames when available.

The first home observation is admitted before the initial native gestation
checkpoint. An intake file alone does not establish model consumption; the
native admission receipt is needed.

Context uses complete contributions within the configured assembled-input
budget. `mindscape.context_focus_profiles` supplies activity preferences;
admission/exclusion reasons appear in context receipts. These are bootstrap
priorities, not learned neural attention. Required input that cannot fit fails
explicitly. The budget is not a physical RWKV recurrent window.

The native Chat receptor currently accepts explicit positive movement,
inspection, file-open and Python-run requests:

```text
Please go to /workshop then open Example.py then run it.
Please open /staging/CaseNotes.txt and /staging/SecondNote.txt.
Please sense .
```

Quote paths containing spaces. Each target retains case and needs its own
verified return. A request traverses actual retrieval/context/native-model
admission before numeric motor release and native SELF authorization.
Speech, remembered text and file contents cannot initiate actions.
Successful goals require a joint checkpoint before public completion.

There is no current Chat opcode for write/mkdir, module activation, web
browsing or sleep. Put an experiment in the workshop before requesting
execution; uploading to staging does not move it there automatically.

## Installed module handler contract

The body has lower-level module handlers, separate from the connected Chat
motor policy. A remembered module can be activated directly from any room
through that handler when authorized; navigation is not a prerequisite unless
`mindscape.modules_require_room=true`. The current bootstrap receptor does
not yet provide this activation route.

| Module | Installed behavior |
|---|---|
| `web_search` | Fetch a complete remote search-results page, including links |
| `web_read` | Fetch a destination and return extracted text with response hash |
| `terminal` | Workshop-scoped command execution in the isolated namespace |
| `sleep` | Invoke the actual attached production dream engine |

The web scripts are text interfaces rather than a graphical/JavaScript browser.
Remote text is reported content, not verified fact or permission to execute
instructions. Web modules declare network access and have no writable home
mount; module/runtime files are read-only.

While a module return awaits consumption, the handler's interface can receive
a context focus boost. Consuming the matching return, another actuator, a new
message, movement, reply, disengagement or restart clears that focus. Activation
is synchronous: there is no persistent background browser or timer-based
disengagement. This focus contract has component diagnostics; the October 17
live body trial did not exercise module search or sleep.

Built-in scripts and intake records are controller-owned. A workshop script
does not install itself as controller code or become a native ability simply
by existing on disk. Older dashboard Module Studio paths still assume
`data_dir/agent_home`; syntax validation there is not capability installation.

## Workshop containment

Python execution requires an actual matching content/hash observation.
`run` opens and hashes the target if the prerequisite is missing; a mismatch
fails rather than executing changed code. Only workshop Python files run.

The working directory is the current workshop directory when already there,
otherwise the script's workshop parent. Bubblewrap exposes read-only
OS/interpreter/runtime files, the writable workshop and temporary namespace
files. Network and process namespaces are isolated. Bedroom, closet, other
rooms, host source and mind stores are not mounted. The inherited native
Python ability is rebound to this handler.

There is no execution timeout or output ceiling and no host fallback. Nonzero
exit, missing sandbox or explicit lifecycle cancellation produces failure.
Shutdown can interrupt only the runtime's own sandbox process namespace.
Workshop artifacts persist in the workshop; this does not authorize writes
to the agent's mind or controller.

## Creation and gestation

The wizard separates identity/archetype, memory depth/voice, credentials/main
channel, tools, safety and schedule. Dashboard needs no channel token; external
channels need explicit enablement and credentials. The default native route
uses local RWKV and local Ollama embeddings, without a model API key.

Archetypes `balanced`, `curious`, `deliberate` and `builder` choose native
taste records/preferences through the configured dependency's actual gestation
interface. They do not train weights or establish competence.

`creation.json` in persistent data and `identity.json` in the home record
the selected identity, archetype and channel without credentials. Provisioned
status is pending until native startup verifies/gestates a matching profile
and records the joint generation. Legacy resumes without a creation contract
retain their original native profile. Do not rewrite an established identity
by changing setup values.

Configure `mindscape.home_parent` for another home parent; the CLI has
`--agent-home` and `--data-dir`, but no `--home-parent` flag.
Use a distinct name/home/data lineage for a new agent.

The bedroom sleep descriptor invokes the attached production
`BackgroundDaemon.run_dream_cycle` when called through its handler; a missing
engine or reported error fails explicitly. This is separate from the
[disconnected nursery prototype](nursery_status.md), whose sleep writer does
not yet match canonical store schemas.

## Verification scope

The [October 17 live record](audits/2026-10-17-native-body-operational/README.md)
verifies actual movement, full file opening/hash read-back, isolated Python
execution and graceful restart through the current production route. A separate
earlier control verified sensing while a script was running. Focus, handler
interfaces and web modules also have isolated implementation checks.

No search-provider evaluation, production sleep-learning result, learned motor
development or general conversational-coherence result is established by those
checks. Use Dashboard **Environment and actions**/`/api/motor` for actual
body returns; the staging endpoint targets the selected `mindscape.home`.
