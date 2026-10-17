# Benchmark and diagnostic outputs

**Reviewed: 2026-10-17.** This directory holds generated experiment artifacts.
JSON/Markdown outputs and run subdirectories are normally ignored by Git;
this README is tracked. Scripts in `scripts/` and `tests/` use different
compositions, so sharing this output folder does not make their results
comparable or full-product evidence.

## Current product evidence

The [October 17 native-body record](../documents/audits/2026-10-17-native-body-operational/README.md)
has a composition manifest and per-request receipts for its stated
movement/open/run and graceful-restart workflow. It assigns no recall,
coherence, developmental-growth or aggregate performance score.

For a new product evaluation, use normal production ingestion, persistent
memory, all enabled retrieval/reasoning lanes, the production context compiler,
declared model and real output/action path. Record source/dirty state,
configuration, checkpoints, stores, hardware, constraints and grader/outcome.
Per-case receipts and independent outcome read-back are required.
See the [test guide](../tests/TEST_SUITE_README.md).

## Isolated memory-adapter diagnostics

These retained scripts do not establish parity with the current native
Mindscape composition:

| Runner | Scope |
|---|---|
| `tests/locomo_deep_memory_sandbox.py` | Synthetic dialogue/association fixture, adapter ingestion and reader |
| `tests/longmemeval_sandbox.py` | Fresh temporary stores per selected question, adapter retrieval and Codex/Ollama reader |
| `tests/ragoffice_parity_sandbox.py` | Frozen generated exam, isolated Helix retrieval and matched external reader rules |

Even an adapter's “connector” replay does not prove that the current normal
runtime, persistent native state, nine Loom lanes and context/model admission
were used. Do not use these results as native-product scores, final-product
tuning signals or comparisons against another product.

Dry-run examples validate assembly only:

```bash
venv/bin/python tests/locomo_deep_memory_sandbox.py --dry-run
venv/bin/python tests/longmemeval_sandbox.py \
  --dataset /path/to/longmemeval_s_cleaned.json --dry-run
```

Read each script's help and composition before model execution. The LongMemEval
development adapter retains a 100-question ceiling and fixed-seed selection;
that inherited diagnostic limit is not a user-selected final-product budget.
Other harness output/context/iteration limits also require audit.

The LongMemEval adapter can retain:

- `manifest.json`: dataset hash, selected cases, provider/model and settings.
- `details.jsonl`: predictions, injected context and per-case diagnostic data.
- `hypotheses.jsonl`: question IDs and hypotheses.
- `manual_review.md` and `review/*.md`: source/gold/prediction review pages.
- `summary.json`: string metrics and retrieval diagnostics.

Those artifacts help inspect that adapter; they do not fill a missing
production evidence chain. Automated exact match, overlap and support metrics
remain diagnostic unless the declared full-product composition and grading
route are proven.

## Historical results

The [context-fork study](../documents/context_architecture_experiments.md)
preserves the August 8 synthetic-exam numbers and original branches. Those
numbers belong to the isolated adapter study, not today's native agent.
Retain original outputs as provenance; label a mismatched result as diagnostic
and remove it from current product conclusions.
