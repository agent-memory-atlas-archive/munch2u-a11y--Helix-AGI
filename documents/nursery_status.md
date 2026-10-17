# Nursery integration status

**Source review: 2026-10-17 · Status: separate prototype, not a production
creation or training stage.**

Normal CLI setup, the graphical wizard and `main.py` do not call
`core.agent_creation.run_functional_nursery_gestation`. Native gestation
initializes identity/preferences and a joint checkpoint independently.
The creation UI does not currently provide an integrated nursery choice.

## What exists

`core/nursery/` contains a digital sandbox, curriculum, caregiver, growth
tracker and cycle simulator. The separate helper can run cycles and attempt
to write a developmental report card and creation metadata.

The curriculum intends to introduce orientation, utility use, scratchpad
persistence and autonomous inspection/dialogue. The default
`build_grounded_reflex_generator` is a host-coded response policy. It lists
real directories and can write/read scratchpad files, but it is not RWKV
generation or learned motor development.

Supplying an `agent_generate_fn` makes the helper label its report
“Live Neural Model Gestation.” That label does not prove which model ran,
which memory/context lanes it used, that actions executed, or that any learning
persisted. The report's wording is not an evaluation receipt.

## Known unresolved boundaries

| Area | Current implementation |
|---|---|
| Utility execution | `DigitalSandbox.execute_utility` returns simulated output/return codes, including canned success for unknown commands; no actual program execution is established |
| Scratchpad containment | Filenames are joined without production containment checks; traversal can escape the helper workspace |
| Sleep beliefs | The simulator writes dictionary-style entries while production category files use lists; normally seeded stores can raise `TypeError` |
| Sleep journal | Appended rows omit production checksum/schema requirements and can be skipped by the normal journal loader |
| Consolidation | Helper file writes are not the attached production `BackgroundDaemon`/Curator cycle |
| Growth grading | Keywords and cycle-dependent constants can increase milestone scores; verified action receipts and later retrieval are not required |
| Neural learning | Neither a report card nor recurrent intake proves learned motor selection or RWKV weight training |

These findings are documented as source/component diagnostics in the
[October 17 review](audits/2026-10-17-followup-review/findings.json).
They were not repaired or used as training in the later operational-body trial.
Do not run this helper against a lived agent's production stores as though it
were a safe integrated nursery.

The real workshop sandbox in `core/mindscape_workspace.py` is a different
implementation. Its Bubblewrap execution and observed-hash boundary do not
apply automatically to `DigitalSandbox`.

## Requirements before integration can be claimed

1. Connect an optional creation choice to the normal setup/runtime path without
   overwriting an existing agent's identity, lineage or canonical stores.
2. Use the actual production receptive/context/model/body route for action
   attempts. Simulated utilities and host-coded responses must stay labeled
   as component fixtures.
3. Enforce path/process containment and use canonical journal/belief writers,
   source provenance and the production consolidation interface.
4. Record each obligation, authorized action, actual return and independent
   postcondition. Preserve explicit failures rather than converting narration
   or a keyword into success.
5. Verify durable outcomes through restart and later retrieval, then assess
   development through the exact current full system with a composition
   manifest and per-case receipts.

This is unfinished integration work, not a claim that these requirements have
been implemented. See [current architecture](architecture_current.md) and the
[operational-body evidence](audits/2026-10-17-native-body-operational/README.md)
for the runtime that actually executed.
