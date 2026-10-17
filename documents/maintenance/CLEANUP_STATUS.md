# Cleanup branch status

Baseline: `a43492e68c0e7413eca71cd34814c15910cc314e` (October 17, 2026).
The [initial review](CLEANUP_REVIEW.md) describes that baseline; its read-only
statements refer to the assessment before this implementation branch.

## Implemented

- Explicit test-group inventory covering root, prototype and plugin test modules;
  new, stale or duplicate classifications fail. Historical script-runner behavior
  remains available. Live/model tests require an explicit group and opt-in.
- Offline GitHub Actions gate on Python 3.11 and 3.12, using a small independent
  development requirements file. This is maintenance coverage, not a native
  product or all-tests gate.
- Read-only health checker with structured results, nonzero required-failure
  status and no unconditional readiness claim. It never loads weights or
  provisions agent state.
- Shared native-source and model default discovery. Configured activation rejects
  already imported foreign native modules, including submodules. The bicameral
  provider uses the selected source instead of inserting a personal host path.
- Read-only verification against the native source hashes in the preserved
  operational manifest, including recorded uncommitted source changes.
- Native configuration rejects conflicting task-cognition environment overrides;
  the native controller also keeps the legacy task route off.
- Explicit Mindscape CLI provisioning calls the same creation service as the
  wizard. Custom homes are validated before provisioning and retained on reruns;
  nested configuration updates retain existing native dependency/home settings.
- Dashboard room, staging, module and motor paths resolve one selected agent.
  Checkpoint position is read through LATEST.json with SQLite read-only mode;
  no agent is chosen by first directory match. Directory creation is deferred
  to explicit upload/module writes. Restart the dashboard when changing agents.
- Shared message chunking across all five channels, preserving their limits and
  existing five-chunk ceiling, plus shared wizard credential parsing.
- Tool registry construction extracted behind the existing executor method.
  Schemas, handlers, availability rules and execution remain unchanged.

## Verified locally

- Offline gate: **100 passed, 13 subtests passed**, Python 3.12.14.
- Six additional existing creation/identity diagnostics passed (three native/CLI
  cases outside that selection were deselected).
- All **85 tool registrations** matched the baseline in a separate comparison:
  schema, toolset, bound handler, availability-check name, required environment,
  description and focus type. No registered tool was executed by this comparison.
- Every tracked Python file parsed; shell scripts retained valid syntax.
- No changes under documents/audits/, Over_Agent_Design/ or core/nursery/.
- No model inference, live channels, agent data migrations or history rewrites.

An initially broader creation-test selection also selected a GUI test and hit
missing PyQt6. The six filesystem/identity checks were then run by their specific
class and passed. GUI behavior has not been certified here.

## Remaining gates and deferred work

The native test group returns BLOCKED (exit 2): the real MightyMem checkout,
Torch/Transformers, checkpoint weights and services are absent here. The source
verifier adds a reproducibility check; it is not a newly verified dependency
release, a complete native dependency lock, or a live native result.

Before merging native-source/configuration changes, run the native group and
isolated operational invariants from the review using the intended dependency,
weights and sandbox. Review a custom-source launch, cancellation, checkpoint
completion, restart, recipient routing and native task isolation in that setup.

Retained integration tests still contain baseline contract drift: health-check
API drift is repaired, but PulseContext wording/provenance expectations and
other older API assumptions have not been weakened or blanket-updated. The
integration, prototype, plugin and live groups are not reported as passing.

Camera/journal and pending-queue extraction, major PulseLoop/Preconscious splits,
root packaging, prototype retirement, and evidence relocation remain separate
work. Their hardware, concurrency, persistence or native acceptance gates are
not available in this environment. Preserve the current audit evidence and
stored formats when continuing; do not merge retrieval lanes or action routes.

## Review and rollback

Review the commits in order: validation, source/configuration, selected-agent
paths, shared helpers, registry wiring, and this status record. Each can be
reverted independently in reverse order. There are no persistent-store schema
changes or automated data moves. Reverting the path fixes restores the prior
UI/CLI behavior; it does not remove any user files created through the UI.

For later changes that do affect agent state, use a consistent offline or
supported database backup of the selected home, canonical memory and full joint
lineage. Keep credentials separate and never commit them. A passing offline
smoke gate does not replace that preparation.
