# Local mindscape launcher

The selected application is this Helix checkout. The authoritative entry point
is `main.py`, using the existing standard `PulseLoop`. `core/mindscape.py` adds a
gestation, synchronization, and context adapter; it does not replace Helix with
MightyMem's standalone console or autonomous loop.

## Setup

```bash
venv/bin/python -m pip install -r requirements-mindscape.txt
venv/bin/python setup.py --composition mindscape --composition-only \
  --mightymem-path ../MightyMem \
  --rwkv-model ../habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29
venv/bin/python main.py --check-setup
venv/bin/python main.py
```

The configuration-only command preserves credentials and lived memory. For a
new agent, omit `--composition-only` to run the existing bootstrap as well.
Use `--workspace PATH` to select the native workspace. `--resume-only` makes a
missing joint checkpoint an error instead of permitting first gestation.

`config/config.json` owns `composition`, `local_model`, `local_context_window`, and the nested `mindscape` paths. The primary default runtime is the **Bicameral Dual-RWKV System**, uniting the recurrent Habitus memory cortex with the Bicameral RWKV-7 speaking model and Learned Vocabulary Membrane Grounding. For users preferring Ollama, local Granite (3B or 8B) remains supported as an optional foreground language provider. The pinned RWKV checkpoint is verified by MightyMem before loading.
The supported joint bridge runs on CPU. Transformers 5.17 is pinned because
the checkpoint's cache API requires at least 5.15.

## Runtime connections

| Component | Live role |
|---|---|
| Helix PulseLoop | Cadence, events, foreground session, actions and post-pulse hooks |
| Native mRAG / Context Office | Semantic retrieval and evidence selection over Helix memory |
| Helix physics | 8D attention, beliefs, associations and affect |
| MightyMem ContinualMind | Joint persistent RWKV/cortex state and Habitus graph |
| RWKV | Incoming events, own foreground output and actual return tokens; native cortex coupling |
| Context Loom | Additional persistent evidence lanes and final pulse-context compilation |
| Dual RWKV-7 (Subconscious + Speaker) / Optional Granite | Bicameral foreground language, subconscious motor affordances, and natural intentions |

The native graph and Loom SQLite connections have one owning thread. Source
paths and source hashes are recorded so a different installed `context_loom`
package cannot silently stand in for the configured MightyMem source.

## Gestation and synchronization

State belongs to `data/mindscape/`, separate from existing Helix stores and older
experimental checkpoints. On first launch, the native runtime gestates the
cortex/graph and loads the pinned RWKV weights. On later launches it restores
the joint checkpoint and validates the saved tensor state and trained weights.
No older experiment is automatically adopted as this agent's lineage.

The adapter projects canonical Helix records with original source IDs, content
hashes and evidence labels. Repeated synchronization skips identical records;
changed records create linked versions. Historical records are indexed without
being replayed as fresh human feedback or RWKV gradient training. Private
thoughts remain private and historical success labels cannot become verified
observations. Helix's original files remain authoritative.

The first gestation is checkpointed before historical indexing begins. Native
Loom logging populates its X/Y state and entity graph as well as its record
store. Completed projections are marked so a normal restart does not index
them twice. Exactly-once graph activation across a crash during indexing has
not been established.

The native joint checkpoint includes RWKV state, cortex state, coupling weights,
graph database and checksums. Checkpoints are retained by the native runtime;
they consume disk space as the agent continues. Loom is a derived projection
and is reconciled with the canonical corpus after restart.

RWKV gradient training is disabled in this adapter. It advances recurrent state
and couples it to the native cortex; it does not run MightyMem's standalone
continual-learning or motor-emission loop. This distinction remains visible in
the composition receipt.

### Functional Nursery Gestation (Pre-Contact Sandbox)

Before engaging in live external communication or host operations, newly gestated
agents execute a functional, 4-stage developmental sandbox via
`core/agent_creation.py::run_functional_nursery_gestation()` and `core/nursery/`:

1. **Stage 1 (Sensory-Motor Reflex)**: Validates basic motor impulses and perceptual responses.
2. **Stage 2 (Scratchpad Persistence)**: Validates persistent internal scratchpad I/O and state maintenance across pulses.
3. **Stage 3 (Workspace Mutation & Tool Verification)**: Exercises native file mutation (`write`, `read_back`) and execution receipts in an isolated digital sandbox.
4. **Stage 4 (Attuned Dialogue)**: Validates multi-turn conversational grounding and identity continuity.

Results are recorded in `data/agents/<agent_id>/developmental_report_card.txt` and preserved in `creation.json`.

## Receipts and verification scope

Pulse context uses conditional source headings through `core/pulse_context.py`
and `core/mindscape_context.py`. Fresh messages and sensations, focused-work
results, recalled context, prior assistant statements, and internal state are
separate. Only populated sections appear. A remembered observation remains
historical, and an earlier assistant statement remains unverified. The latest
complete private foreground thought has an explicit continuation slot; outward
replies never populate that slot. Earlier private records can surface as labeled
cognitive context. Provider history retains actual received messages and
delivered replies; retrieved pulse packets are transient. The installed Granite
foreground sees delivered replies in matching JSON message envelopes, while raw
dialogue remains unchanged. Canonical record types own the recalled sections,
including after nominations from different lanes are merged. Older assistant
prose is recalled only for a request about past statements; actual dialogue
history remains available. The installed Granite
tokenizer counts the complete system/dialogue/pulse request. Provider pruning or
a generation that reaches its context boundary causes an explicit failure.

The Loom presentation override participates in native admission/token counting
and packet hashing. Retrieval lanes, evidence policies and configured budgets
remain native; altered header costs can affect what fits in that budget.
Selected historical observations are rendered with their source and verification
labels (the upstream section order previously omitted the observations section).

The typed compositor takes fresh query text separately from recalled material,
state and output direction. Each mRAG result keeps its actual sentence-head
provenance. A uniquely matched passage may receive an italic, tagged recollection
directly afterward. Ambiguous/missing anchors retain their ordinary source
section. Canonical input and remembered text are not rewritten; rendering alone
adds asides, with source hashes and original offsets recorded in
`pulse_context.context_assembly`. Identical canonical IDs/content from mRAG and
Loom are displayed once, with the duplicate explained in the receipt. No
retrieval score establishes a contradiction or overrides current permission.

The Mindscape profile removes the first-four-sentences restriction from sentence
head generation. Derived heads, candidate selection, recent-memory selection,
and history compression retain inherited policies. They remain prerequisites for
the full-system boundary audit. Loom counts the entire rendering against the
remaining physical input allowance after provider history and system overhead,
and fails explicitly if required content cannot fit.
No agent behavior improvement is established by these implementation checks;
see the [context weave audit](audits/2026-10-10-context-weave/README.md).

`data/mindscape/composition-manifest.json` records sources, configuration, model
identities, stores, lanes and integration boundaries. `receipts.jsonl` records
initialization, canonical sync, pulse context/state changes, foreground returns
and checkpoint hashes. Native restore evidence lives in `joint/events.jsonl`.
GUI launch output is retained in `logs/launcher.log`.
Dependency and bootstrap failures stop GUI setup, with bootstrap details in
`logs/bootstrap.log`. Closing the launcher sends a graceful shutdown request;
the process finishes initialization or its current pulse before closing state.

`--check-setup` loads and synchronizes the actual composition, then exits without
starting channel services or passive sensors. This is initialization evidence,
not a recall, action, learning or competence benchmark. Inherited Helix retrieval,
provider and orchestration limits still need a complete audit before behavioral
scoring. The new adapter adds no record-sampling, action, or reasoning ceiling.

### Subconscious motor actuation and workspace abilities

The installed bootstrap provides a native workspace body with move, sense,
open, write, mkdir and run abilities. Rather than constraining the foreground
Speaker to output rigid `<intention>` JSON markup, Helix uses the
**Subconscious Motor Actuation Bridge**:

- **Motor Affordance Impulse**: The Subconscious stream emits latent motor
  affordances through `OutputTrunk.DO` and `OutputTrunk.LOOK`
  (`core/mindscape.py::has_subconscious_motor_impulse()`).
- **Natural Intention Extraction**: When the Speaker articulates natural prose
  or commitment (e.g., *"I will check `main.py`"*),
  `core/mindscape_intention.py::parse_natural_or_wire_intention()` resolves the
  intended target and action, with seamless fallback to wire JSON if emitted.
- **Physical Execution & Authoritative Receipts**: The native SELF kernel selects
  and authorizes the corresponding workspace handler (`resolve_subconscious_action()`).
  Sense reads attributes without content; open reads UTF-8 or extracts PDF text.
  Writes require read-back verification; Python execution captures observed hashes
  and stdout. Python runs in an isolated workspace with no host network.
  Authoritative receipts are recorded in `receipts.jsonl` and fed back into the
  recurrent tensor state.
The latest real launcher failures and repairs are preserved in the
[native-cycle audit](audits/2026-10-10-native-cycle-repair/README.md).

The [2026-10-09 launch audit](audits/2026-10-09-mindscape-launch/README.md)
records real startup, synchronization, restart and pulse diagnostics. Those
checks passed their stated infrastructure conditions. The observed dashboard
message produced a private thought but no delivered reply, so this is not a
claim that the complete agent is ready for unattended use.
