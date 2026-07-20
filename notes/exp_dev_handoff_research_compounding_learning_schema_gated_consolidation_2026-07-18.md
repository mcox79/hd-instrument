# exp_dev hand-off — research: compounding-learning missing-structure drill

**Filed-by:** research (Sonnet lit-scan x3 + director synthesis), 2026-07-18.
**Trigger:** `notes/research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md` — the
5x biology-led drill diagnosing WHY learning does not yet compound (flat re-reading, null curriculum order,
budget-flat CLS replay, no schema-selection headroom). Read that note in full before designing any cell; it
contains the mechanism citations, the ranked verdict, and the exact HARD-PASS/HARD-FAIL bands below.
**Pause state:** respect `data/orchestrator_paused.flag` if present — do not ship without checking.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off gives anchor pointers and why-now context, NOT a
prescribed cell implementation. exp_dev owns cell design, pre-reg, smoke gate, and dispatch.

## Anchor candidates (rank-ordered)

1. **Schema-fit-weighted consolidation-cost allocator vs. flat-% rehearsal sweep** (Prediction A in the research
   note). Reuses the ALREADY-LANDED SRColumnSolver resolvent (`experiments/exp_grounding_multihop_sr_reachability_routing_v1.py`)
   for pairwise schema-fit, per the already-diagnosed fix in `research_schema_fit_derivability_signal_upgrade_2026-07-16.md`.
   Tier hint: MEDIUM effort (mostly a reallocation of an existing rehearsal-sweep harness, not new machinery).
   Why now: directly explains negative #3 (flat-% CLS sweep showing ~0 benefit below 25-50%); the cheap decisive
   test in the research note (re-bucket EXISTING sweep results by schema-fit of rehearsed items, zero new compute)
   should be run FIRST as a free confirm/kill signal before building the explicit allocator.
2. **Reactivation-triggered reconsolidation pass** (Prediction B). Needs the confidence/permanence scalar already
   scoped in `research_consolidation_confidence_permanence_relational_inference_2026-07-14.md` (not a new
   invention — check whether that scalar already exists on disk before building it fresh). Tier hint: MEDIUM-HIGH
   (new mechanism: re-evaluate schema-fit/local-surprise on RE-touch of an already-written entry, allow gated
   overwrite). Why now: directly explains negative #1's specific "resurfaced but got the meaning wrong" detail,
   which a one-shot write-time gate structurally cannot fix. Cheap decisive test first: re-check the EXISTING
   re-reading negative's wrong-meaning cases against whether those entries were previously-written (old, never
   revised) vs. genuinely new misses — zero new compute, on-disk data.
3. **Local/schema-conditioned surprise fix** (Rank 3 precondition, already diagnosed in
   `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` — raw_PE should be computed
   against the same local reachable-neighborhood schema_fit already scans, not a flat corpus-global rank). Tier
   hint: LOW-MEDIUM (a redefinition of an existing scoring function, not new architecture). Why now: input
   precondition for anchors 1 and 2 to fire on the right items; can be built/tested in parallel, does not block
   anchors 1-2 from starting.
4. **The fair efficiency test itself** (capture-per-pass-per-verified-residual at foundation-size N vs 2N, matched
   difficulty, externally-reviewed residual). This is the DECISIVE test for the whole verdict, not a build item —
   flag for exp_dev to scope as the final confirmatory cell once anchors 1-3 have candidate implementations,
   using the HARD-PASS/HARD-FAIL bands given verbatim in the research note's efficiency-test section.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md` (this drill's
  full note — ranked verdict, all citations, honesty/calibration section)
- `notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md` (pairwise schema-fit fix, reuses
  `experiments/exp_grounding_multihop_sr_reachability_routing_v1.py` SRColumnSolver)
- `notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` (local-vs-global surprise
  diagnosis)
- `notes/research_consolidation_function_inventory_schema_reorg_2026-07-16.md` (write-time-vs-reorganization
  function split; confirms reconsolidation is a genuine, previously-unbuilt gap)
- `notes/research_consolidation_confidence_permanence_relational_inference_2026-07-14.md` (confidence/permanence
  scalar scoping, reconsolidation precedent — check before building a new scalar)
- `notes/research_curriculum_order_corpus_mismatch_brain_check_2026-07-16.md` (negative #2 already explained as
  corpus-mismatch, NOT part of this hand-off's scope — do not re-test curriculum order here)
- `hdlab/additive_map.py` (score_all — existing surprise/prediction-error scoring primitive)
- `hdlab/reachability_audit.py` (existing schema-fit/composability metric)

## Contract

- exp_dev authors + smokes locally, returns the exact `queue_add.sh` dispatch command; orchestrator ships +
  REMOTE VERIFIES post-ship, per locked ship policy.
- Pre-register per envelope-fail-bands; the HARD-PASS/HARD-FAIL numbers in the research note's Prediction A/B/C
  sections are usable verbatim as pre-reg thresholds — do not loosen them without a stated reason.
- Run the two zero-compute "cheap decisive test" re-analyses (bucket-by-fit on existing sweep data; check
  wrong-meaning cases against previously-written status) BEFORE authoring any new cell — they are free kill
  signals per the research note.

## Autonomy declaration

exp_dev owns: which anchor to build first among 1-3 (the research note ranks them by explanatory power, not
necessarily by build-ease — exp_dev may reorder for cheapest-first), exact cell architecture, smoke design, and
whether the two zero-compute re-analyses warrant a full build at all (if the free re-bucket/re-check show no
latent signal, that is itself a valid kill decision, reportable back through the normal verdict path).
