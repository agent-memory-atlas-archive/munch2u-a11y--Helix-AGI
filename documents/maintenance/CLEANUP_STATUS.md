# Cleanup branch status

Baseline: `a43492e68c0e7413eca71cd34814c15910cc314e` (October 17, 2026).
Updated: October 18, 2026. Branch: `cleanup/careful-consolidation`.

The [initial review](CLEANUP_REVIEW.md) describes the baseline; its read-only
statements refer to the assessment before implementation. The branch remains
separate from main and is presented in draft PR #10.

## Implemented

- Explicit test-group inventory covering root, prototype and plugin test modules;
  new, stale or duplicate classifications fail. Historical script-runner behavior
  remains available. Live/model tests require an explicit group and opt-in.
- Offline GitHub Actions gate on Python 3.11 and 3.12, using small independent
  development requirements, plus Node request/DOM regressions. A separate Linux
  Python 3.12 job installs the wizard profile and runs offscreen Qt diagnostics.
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
  to explicit writes. Restart the dashboard when changing agents.
- Shared message chunking across all five channels, preserving their limits and
  existing five-chunk ceiling, plus shared wizard credential parsing.
- Tool registry construction extracted behind the existing executor method,
  preserving declarations, availability rules and dispatch wiring.
- Shared requirements groups preserve the original full-install declarations.
  The launcher installs a lighter wizard profile before runtime selection,
  checks the chosen Python environment and propagates dependency failures.
  See [dependency profiles](DEPENDENCIES.md) for scope and deferred locking.
- Shared wizard provider rules align credentials, Models and bootstrap. Native
  RWKV is retained instead of silently switching to Ollama or a stale provider.
  Users can select the separate Helix composition; unimplemented primary
  providers are blocked. Explicit data/source/home/model choices reach bootstrap.
  Existing channel credentials survive model edits and bootstrap retains the full
  enabled channel list while adding the selected primary. Public JSON excludes token
  fields, and invalid saved configuration is retained with an error.
- Headless or unavailable-Qt launches forward to CLI setup with arguments and
  exit status preserved. The dependency progress timer remains owned until
  completion; a failed install never proceeds to bootstrap.
- Module Studio source reads and staged-file removal use valid request URLs.
  Removal buttons bind actions directly, including filenames with apostrophes.
  Request failures are checked before consuming success data or refreshing.
- Module creation validates names/code, rejects collisions instead of overwriting
  existing modules and resets line counts between files.
- Canvas API and tool share payload validation and atomic state replacement.
  Unsupported, malformed, nonfinite or oversized stored payloads are rejected.
  Tool output follows the selected data directory, matching the dashboard;
  history remains capped at 50 entries. Canvas tests no longer write repo data.

## Validation evidence

GitHub Actions for the dashboard implementation commit
`af63c3f3c14a4e7e2600e2cce912914a9431e007` passed:

- **124 offline Python tests** on both 3.11 and 3.12 (plus subtests).
- **5 Node tests**: whole module-script syntax, module loading, staged deletion,
  apostrophe filenames and upload request/error handling.
- **7 offscreen Qt/creation tests**, including runtime selection, stale credential
  precedence, unsupported-provider rejection and dependency-install failure.

The workflow continues to run these gates on subsequent commits. They exercise
real Python routes and selected frontend functions with isolated fixtures;
they do not constitute a visible-browser or complete installer run. Installer,
model and service calls in wizard diagnostics are mocked. CI also verifies that
the wizard dependency profile resolves and imports on its Linux runner.

Earlier local validation during the initial extraction passed 100 offline tests,
13 subtests and six selected creation/identity diagnostics. All 85 tool
registrations matched baseline metadata during registry extraction; no tool was
executed by that comparison. Python parsing and shell syntax were checked then.
Current shell syntax is also covered by the offline gate.

No changes were made under documents/audits/, Over_Agent_Design/ or core/nursery/.
No model inference, live channel actions, agent data migrations or history
rewrites were performed. Local execution became unavailable during the expanded
wizard/dashboard work; those changes were verified through GitHub Actions.

## Remaining gates and deferred work

The native test group was BLOCKED (exit 2) in the local assessment: the real
MightyMem checkout, neural dependencies, checkpoint weights and services were
absent. The source verifier adds reproducibility checking; it is not a newly
verified dependency release, full native dependency lock or live native result.

Before merging native-source/configuration changes, run the native group and
isolated operational invariants from the review using the intended dependency,
weights and sandbox. Review a custom-source launch, cancellation, checkpoint
completion, restart, recipient routing and native task isolation in that setup.

A visible wizard/browser walkthrough, clean full-runtime installation,
macOS/Windows checks and live provider/channel validation remain open.
The full-runtime compatibility requirements still include optional backends;
further reduction needs import/runtime acceptance coverage. No speculative
package upgrades or substitute dependency revisions are included.

Retained integration tests still contain baseline contract drift, including
older PulseContext wording/provenance expectations. The integration, prototype,
plugin and live groups are not reported as passing. Selected deterministic
desktop/canvas tests were isolated and moved into the offline group.

Camera/journal and pending-queue extraction, major PulseLoop/Preconscious splits,
root packaging, prototype retirement and evidence relocation remain separate
work. Preserve audit evidence and stored formats when continuing; do not merge
retrieval lanes or action routes.

## Review and rollback

Review focused commits by concern: validation, source/configuration,
selected-agent paths, shared helpers, registry wiring, dependency profiles,
wizard fixes and dashboard fixes. Revert dependent commits in reverse order.
There are no persistent-store schema changes or automated data moves. Reverting
path fixes restores prior behavior without removing files created through the UI.

For later changes affecting agent state, use a consistent offline or supported
database backup of the selected home, canonical memory and full joint lineage.
Keep credentials separate and never commit them. A passing offline gate does
not replace native acceptance.
