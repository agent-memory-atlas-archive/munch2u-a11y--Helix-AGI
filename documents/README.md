# Helix documentation

**Reviewed: 2026-10-17 · Source: `main` plus current working-tree changes.**
Guides describe current source. A source review, initialization check or unit
test does not establish product competence.

## Current references

| Document | Purpose |
|---|---|
| [Project README](../README.md) | Overview, startup and verified/unfinished boundaries |
| [Current architecture](architecture_current.md) | Native ownership, memory/context/model flow, actions and persistence |
| [System manual](../SYSTEM_MANUAL.md) | Operator workflow and subsystem/configuration reference |
| [Mindscape launch](mindscape_launch.md) | Dependencies, named creation, CLI provisioning gap, startup and shutdown |
| [Action paths](action_path.md) | Numeric native body contract and separate legacy routes |
| [Agent home](agent-home.md) | Rooms, sensing, module-handler limits and workshop containment |
| [Nursery status](nursery_status.md) | Disconnected prototype, persistence/safety gaps and integration requirements |
| [Test guide](../tests/TEST_SUITE_README.md) | Implementation diagnostics and full-product evidence requirements |
| [Models](../models/README.md) | Pinned RWKV, embeddings and optional model files |
| [Developer examples](../examples/README.md) | Isolated API demonstrations, not the full native runtime |
| [Task cognition](task_cognition_pipeline.md) | Separate legacy focus-worker route; disabled in native Mindscape |

Use executable source to resolve wiring discrepancies. For behavioral claims,
require the exact declared composition, real entry point and output path,
per-request receipts and verified outcomes. Tests and source alone do not
outrank contradictory live evidence. Architecture is the canonical wiring
reference; the manual and README should agree with it.

## Recent operational evidence

[October 17 native-body record](audits/2026-10-17-native-body-operational/README.md)
links the composition manifest, actual model-context admission, matching
action returns, independent file/artifact read-back and joint checkpoint.
It covers a normal launch, graceful restart and move/open/run work on the
CPU RWKV profile. The 72 focused implementation checks are separate diagnostics.

This is not evidence of learned autonomy, broad conversational coherence,
factual-recall accuracy or nursery-driven growth. Earlier October 17 trials
with auxiliary-routing or checkpoint mismatches remain diagnostic provenance,
not substitutes for the final handoff composition.

## Historical audits and design work

[`audits/`](audits/) preserves dated source reviews, reproductions, failing
trials and implementation checks. Statements such as “latest,” “paused,”
“current” or “passed” inside those snapshots refer to their original source/date.
Do not apply them to a changed runtime without verifying its composition.

- [October 10 diagnostic handoff](mindscape_diagnostics_2026-10-10.md)
- [Earlier integration plan](mindscape_implementation_plan.md)
- [Older module audit index](audits/audit_overview.md)
- [Over-Agent design](../Over_Agent_Design/README.md): separate design/prototype material.
- [Design reflection](design_reflection.md): creative framing, not a technical or experience claim.

Old natural-intention, wire-format, provider-tool and focus-worker documents
do not define the current native motor route. The nursery's report cards and
isolated “live model” helpers do not establish full-product learning.

## Benchmark records

These are historical or isolated adapter studies, not evaluations of the
current native Mindscape composition:

- [LoCoMo retrieval report](locomo_benchmark_report.md)
- [Unified retrieval report](unified_retrieval_report.md)
- [Context-compiler fork comparison](context_architecture_experiments.md)
- [Benchmark reports](benchmark/)
- [Benchmark output guide](../benchmark_results/README.md)

Preserve original measured outputs as provenance. If a study bypasses the
current production ingestion, memory lanes, compiler, model or action/output
path, its numbers cannot be used as current product scores or comparisons.

## Maintenance rule

Changes to runtime wiring, providers, stores, context admission, actions or
lifecycle should update architecture and the relevant operator guide together.
Keep current support, observed behavior, implementation diagnostics and planned
work distinct. Do not silently turn a failed historical run into a success.
