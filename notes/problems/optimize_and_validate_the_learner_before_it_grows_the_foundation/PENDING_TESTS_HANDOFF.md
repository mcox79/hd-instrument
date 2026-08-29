# PENDING-TESTS HANDOFF (survives compaction / a problem-switch)

The learner problem's CORE is COMPLETE + folded into `SOLVED.md` (status PARTIAL, WIP until owner_verdict: DONE).
TWO Layer-1 OPTIMIZATION tests are OUTSTANDING (flagged in SOLVED.md's "OUTSTANDING LAYER-1 OPTIMIZATION TESTS"
block). This note lets any later session finish them WITHOUT re-deriving anything. hd_metrics_sync is DISABLED,
so their results need a MANUAL orchestrator pull.

## The two tests
1. **exp_counterfit_taxonomic_structure_v1** -- does injected WordNet taxonomic structure (counter-fit,
   attract synonyms/hypernyms + repel antonyms) GENERALISE to held-out relations + a DISJOINT gold, or only
   MEMORISE? Request: `REMOTE_RUN_REQUEST_exp_counterfit_taxonomic_structure_v1.md` (this folder).
   FIRST-RUN BUG (being fixed by hdi_exp_dev agent a02778f5): FAILED-loud DISCRIMINATOR_TOO_SPARSE -- word-level
   70/30 split left too few disjoint SimLex/WordSim pairs (94/38 < 100; SimVerb 294 OK). FIX = SimVerb-primary
   disjoint gold (report SimLex/WordSim underpowered) OR relation-level split. Do NOT weaken the oracle guard.
2. **exp_recipe_diagnostic_ppmi_svd_knobs_v1** -- is the below-distributional-floor SimLex gap a FIXABLE RECIPE
   (PPMI shift/alpha/eigenvalue-p/subsample knobs) or DATA-LIMITED (gensim matched-15M reference)? Request:
   `REMOTE_RUN_REQUEST_exp_recipe_diagnostic_ppmi_svd_knobs_v1.md`. FIRST-RUN BUG (being fixed by a02778f5):
   --mode default="smoke" -> bare remote invocation ran 150k SMOKE not 15M FULL. FIX = default->"full"
   (bare==FULL invariant). INTERIM EXPECTATION: likely "mostly data-scale" per the curriculum drill.

## Resume steps (any later session)
1. Confirm hdi_exp_dev agent a02778f5 GREENED both cells (self-test + smoke exit 0; recipe-diag: bare==FULL now;
   counter-fit: disjoint gold now powered). If not done, re-check / re-fix per the bugs above.
2. RE-DISPATCH each via the strategy/orchestrator lane (NOT the solver): `python tools/fulfill_remote_run_request.py
   --request notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/REMOTE_RUN_REQUEST_<cell>.md`
   (if a prior prereg/entry exists, use `--rerun`). If only the known swallowed queue_add.sh rc=1 quirk fires,
   re-fire the identical queue_add.sh directly. NO `--allow-*` bypass flags.
3. MONITOR (remote_cpu_queue, sequential). PULL manually (sync OFF; try single-prefix then SH-4 double-prefix
   `data/exp_exp_<name>/`) to local `data/exp_<name>/metrics.json`.
4. FOLD each into SOLVED.md's "OUTSTANDING LAYER-1 OPTIMIZATION TESTS" block, replacing the pending text with the
   verdict + numbers. VET counter-fit if it PASSES (generalise-vs-memorise; a HELD-OUT margin, NOT the covered
   gold -- and CHECK A FREQUENCY BASELINE, the same confound that refuted the is-a drill). recipe-diag is a
   diagnostic (report the map + the one-sentence diagnosis). Re-check `python tools/problem_ledger.py --check`.
5. Do NOT integrate; strategy lands the hdlab diff on owner_verdict: DONE.

## Status at handoff
Cells FIXED + GREEN (self-test + smoke exit 0). RE-DISPATCHED to remote_cpu_queue via orchestrator
(2026-08-29). They run ~15-60 min each, sequentially. When they land, follow "Resume steps" 3-5 above
(manual pull -- sync OFF -- then fold into SOLVED.md's OUTSTANDING block + re-check the ledger). If the
metrics.json for either shows mode=smoke / n_tokens=150012, the recipe-diagnostic re-run still hit the smoke
bug -- re-dispatch with an explicit `--args "--mode full"`. Neither affects the CORE verdict -- they populate
the "what to optimise next" story only. This handoff + SOLVED.md's OUTSTANDING block are the durable record;
nothing here depends on the live session's memory.
