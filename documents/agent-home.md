The agent now has a filesystem home separate from the Helix source checkout,
model weights and persistent mind state. CLI setup and the wizard create it;
Mindscape also prepares it before opening or gestating the native mind.
Guided creation uses `data/homes/<Agent Name>` for the home and
`data/agents/<Agent Name>` for persistent memory and mind state. The folder name
comes from the entered agent name, including spaces or Unicode characters.
`--home-parent` changes the home parent; `--data-dir` selects another persistent
data directory. An explicit `--agent-home` must end with the agent name.

```
Nova/
  thinking/          initially empty, quiet space
  modules/           installed web_search.py, web_read.py, terminal.py
  bedroom/
    sleep.json       points to the installed production dream engine
    closet/          personal files
  workshop/          scripts, experiments and their persistent artifacts
  intakes/           fresh text observations of the agent's surroundings
  home.json          room, module and containment manifest
  identity.json      user-supplied identity and creation/gestation receipt
```

The body starts in `thinking` on its first home attachment. Subsequent restarts
preserve its room. A change from an older workspace records the previous
position in native metadata; it does not move or import repository files.
`mindscape.workspace` remains a legacy configuration field; the embodied body
and the native workspace use `mindscape.home`.

Each awake pulse reads the current room's real filesystem attributes and all
immediate entries without opening their contents. It records that complete
observation under `intakes`, consumes it through RWKV and native LOOK, and
offers it as an independent context contribution alongside conversation,
thinking and retrieval. The first home observation is admitted before the
fresh gestation checkpoint. Native admissions and the context compiler retain
their own receipts; an intake file alone does not prove model inference.

Environment and module context compete as whole items for the selected model's
physical context. Their soft priority profiles are configurable through
`mindscape.context_focus_profiles`. Admission and omission are visible in
context receipts. No source is clipped to make it fit. All unresolved thoughts
and observations remain available; exceeding mandatory physical context fails
explicitly.

A remembered module can be activated directly from any room. Navigation is
useful for discovering modules but is not a prerequisite. A deployment can
explicitly set `mindscape.modules_require_room` to true if it wants that rule.
The native controller still must select the proposed ability before execution.

```json
{"action":"activate","arguments":{"module":"web_search","parameters":{"query":"what I need to investigate"}}}
{"action":"activate","arguments":{"module":"web_read","parameters":{"url":"https://example.com/"}}}
{"action":"activate","arguments":{"module":"terminal","parameters":{"command":"ls -la"}}}
{"action":"activate","arguments":{"module":"sleep","parameters":{}}}
{"action":"disengage","arguments":{}}
```

Search reads one complete remote results page, including links; subsequent
pages and destinations can be opened with `web_read`. The reader returns the
complete extracted text and original response hash. These scripts are text
interfaces, not a graphical browser or JavaScript browser engine. Remote text
is reported content, not verified factual claims or instructions to execute.
The installed scripts run in a namespace with read-only runtime and module
files. Web modules have declared network access and no writable home mount.

While an actual module result awaits consumption, its interface receives a
focus boost and surroundings receive less priority. The process has already
finished. Consuming its matching return, choosing another actuator, receiving
a new message, moving, replying, disengaging or restarting clears module focus.
This is an explicit bootstrap interface, not a learned RWKV attention decoder.
Activation is synchronous; there is no live background browser to abandon or
timer-based disengagement.

The terminal always runs in the workshop. Python scripts can be created there
with `write`, observed with `open`, and run by supplying their observed hash:

```json
{"action":"run","arguments":{"path":"/workshop/my_tool.py","expected_sha256":"hash from the actual open return"}}
```

This activates the sandbox automatically from any room. The script's working
directory is the current workshop directory if the agent is already there,
otherwise the script's workshop parent. Agent-created tools remain ordinary
workshop scripts; activation does not install their code into the controller
or change the mind. Built-in module scripts and observation records are
controller-owned and cannot be replaced through the body's write actuator.

Bubblewrap exposes only read-only OS/interpreter files, the writable workshop,
and temporary namespace files to experiments. Their network and process
namespaces are isolated. The bedroom, closet, other rooms, host source and mind
stores are not mounted. The inherited native Python actuator is rebound to
the same workshop handler. There is no execution timeout or output ceiling;
nonzero exit or an unavailable sandbox returns an explicit failure. There is
no fallback to host execution.

Sleep activates the actual attached `BackgroundDaemon.run_dream_cycle`, using
the production stores and Curator. A missing engine or reported error fails
explicitly. Its learning effects belong to that existing production path;
workshop execution cannot invoke it by importing host code.

Validation is implementation evidence only. Home construction, text intake,
wire format, room persistence, focus lifecycle and namespace construction
have component diagnostics. The real workshop diagnostic executed on the
host and verified an internal artifact, failed external writes, inaccessible
bedroom/source, and unavailable network. The regular session blocks nested
namespace networking with `NETLINK_ROUTE: Operation not permitted`; execution
requires a host session which permits bubblewrap. No fresh full-system agent
trial, search-provider evaluation or sleep-learning evaluation was performed,
so there is no new product behavior result or score.

The creation wizard now proceeds through identity and archetype, credentials
and main communication channel, tools, safety, schedule, and review. It
separately offers starter memory depth and voice wording. Dashboard requires no
channel token; Telegram and Discord require enabled channels and their bot
tokens. The CLI additionally supports Slack, WhatsApp and a generic webhook.
The full Mindscape composition uses local Ollama; it does not need a model API
key. Channel credentials are stored in `~/.config/helix/credentials.env` with
owner-only permissions and are excluded from saved wizard configuration and
creation manifests. Existing credentials do not change the selected provider
or re-enable explicitly disabled channels.

The native archetypes are Generalist (`balanced`), Explorer (`curious`), Careful
analyst (`deliberate`), and Builder (`builder`). These choose native taste
records and gentle output-graph preferences through Habitus's actual `gestate`
function. They do not train model weights, establish competence or guarantee
future behavior. Voice wording and memory depth do not replace this native
preference seed.

```bash
venv/bin/python setup.py
venv/bin/python setup.py --non-interactive --composition mindscape \
  --agent-name Nova --creator-name Morgan --archetype curious \
  --primary-channel dashboard
venv/bin/python main.py
```

`main.py` uses the configured persistent data directory unless explicitly
overridden. The real native constructor accepts `gestation_seed` containing the
agent name, human name and taste schema. This support is installed in the
declared MightyMem source at `habitus_ai/continual_mind.py`; activation rejects a
declared source which lacks the interface. The original native defaults remain
available for other callers that do not supply a seed. Established gestation
cannot be rewritten by changing setup settings; creation checks saved identity
before touching existing state. A different name can create a separate agent.
Legacy resumes without a creation contract retain their original native
profile.

`creation.json` under the persistent data directory and `identity.json` under
the home record selected identity, archetype and main channel, without tokens.
Their status begins as pending until native startup. After native gestation is
checkpointed, or a matching native profile is resumed, the controller records
the actual profile and joint generation. Setup does not label a pending seed
as an already gestated mind or a connected communication service. Send the
first message through the chosen channel to establish its actual reply route.
