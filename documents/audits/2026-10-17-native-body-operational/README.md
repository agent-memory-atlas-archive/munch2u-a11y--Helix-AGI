# October 17 native-body operational record

This directory preserves the recorded CPU RWKV `CedarLive` trial. The
authoritative current-source phase is `handoff/`, launched through normal
`main.py` with no arguments and real dashboard input. Its manifest pins the
Helix working tree, external MightyMem source, checkpoint, stores, retrieval
lanes, compiler, runtime settings and operational boundaries.

## Recorded outcome

The final phase restored identity, room and earlier completed goal IDs, then
performed **move → move → open → run → open**. Each action has native SELF
authorization and a matching return. File contents/hashes and the Python
artifact were independently read back. An attempted host write was denied
and the host sentinel remained unchanged.

The complete compiled context passed through all nine production Loom lanes
and was consumed by the declared native RWKV before motor release. Successful
completion was published after matching joint checkpoint `checkpoint-000010`.
These receipts support this workflow and graceful restart; they do not
establish crash-atomic replay, learned autonomy, general conversation quality,
recall accuracy or developmental growth.

## Evidence

| Artifact | What it establishes |
|---|---|
| [Operational review](operational-review.json) | Scope, controls, paths, dependency changes and limitations |
| [Final manifest](handoff/composition-manifest.json) | Declared final source/configuration/model and boundaries |
| [Runtime composition](handoff/runtime-composition.json) | Production wiring and enabled components |
| [Verified context](handoff/verified-context.json) | Actual compiler/retrieval evidence |
| [Native model admission](handoff/model-context-admission.json) | Complete context hash and recurrent-state admission before actions |
| [Action receipts](handoff/verified-receipts.jsonl) | Actual native authorization and per-target returns |
| [Body read-back](handoff/body-readback.json) | Public goal state and observed returns |
| [Verified checkpoint](handoff/verified-checkpoint.json) | Matching joint state before completion |
| [Verified outcome](handoff/verified-outcome.json) | Independent final workflow/postcondition review |
| [Implementation checks](handoff/implementation-checks.log) | 72 focused checks; implementation diagnostics only |
| [Helix patch](implementation.patch) | Recorded working-tree implementation, including new motor code/tests |
| [Native dependency patch](native-dependency.patch) | Configured dependency worktree, including preserved pre-existing edits |

Earlier controls in this directory recorded
[sensing during script execution](sensor-during-execution.json),
[negation rejection](03-negative.verified.json) and
[graceful shutdown](graceful-shutdown-verified.json).
They have their own source provenance and preceded the final small routing
repairs; they were not all rerun on the final byte-identical source.

## Boundaries and provenance

The motor policy recognizes explicit user commands and emits integer signals;
it is bootstrap scaffolding, not learned neural action selection. Speech has
no actuator authority. Nursery helpers were not part of this composition.
Native and foreground RWKV ran locally on CPU, with local Qwen3 embeddings.
No aggregate product score was assigned.

The selected external dependency was `/home/nemo/MightyMem`, including
cooperative cancellation changes. The native patch also preserves pre-existing
`continual_mind.py` edits and must not be read as wholly authored by this trial.

Sibling `2026-10-17-native-nervous-system/` and
`2026-10-17-native-nervous-system-final/` directories preserve earlier attempts
with auxiliary-route and checkpoint-durability mismatches. They are diagnostic
provenance, not substitutes for this final composition. The `restart/`
subdirectory is an intermediate phase; final-source claims use `handoff/`.

Process IDs, port `15219` and “running” status in saved JSON describe the time
of recording, not a service-availability guarantee. No live evaluation was
rerun for the subsequent documentation cleanup.
