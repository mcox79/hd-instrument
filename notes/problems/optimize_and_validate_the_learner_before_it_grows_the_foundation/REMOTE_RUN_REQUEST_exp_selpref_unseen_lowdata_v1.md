---
cell: experiments/exp_selpref_unseen_lowdata_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 5400
results_path: data/exp_selpref_unseen_lowdata_v1/metrics.json
self_test: green
smoke: green
question: Does FEATURE-BASED selectional preference (thematic fit generalised from the argument's brain-derived features) beat word-identity co-occurrence COUNTING on GENUINELY-UNSEEN (verified zero-count) verb-argument pairs and at LOW token budgets -- i.e. does the brain's feature-generalisation advantage show at the regime where it should (unseen / data-starved), even though counting wins where it has data? Re-runs the exp_exemplar_selpref_v1 MIDDLE_BAND at the correct regime with a richer 65-dim predicted-Binder feature space instead of the 12-dim Lancaster space that was too thin.
gate: PASS iff FEAT_GEN (feature generalisation) beats WORDID_COUNT CI-separated (paired Delta over common items) ON THE UNSEEN / low-data regime, AND FEAT_SHUFFLE (argument-feature rows shuffled across words) + RANDOM both lose CI-separated, AND the CROSSOVER holds (the feature advantage on unseen/low-data shrinks or reverses on seen/data-rich pairs -- the brain signature). Report the richness ablation (BINDER65 vs LANC12) and the pooling ablation (exemplar vs mean-centroid). RIGOROUS_NEGATIVE (a FULL PASS) if features STILL do not beat counting even on genuinely-unseen pairs -- then the feature-generalisation advantage is NOT present in our representation, reported with the MECHANISM reason (not a regime excuse).
kb_referents:
  - data/exp_structured_context_learner_v1/parsed_simplewiki_15000000tok.jsonl
  - data/exp_learner_safety_gate_v1/parsed_simplewiki_150000tok_posfixed.jsonl
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
  - data/corpora/binder/binder2016_ratings.csv
---
# REMOTE_RUN_REQUEST -- exp_selpref_unseen_lowdata_v1 (fidelity phase 3, DRILL #6: feature-generalisation at the BRAIN'S regime)

Solver-dropped request; the strategy/orchestrator lane runs the fulfiller (validates, writes prereg, ships code+data, queues CPU). Re-run of a strong LOCAL full-N preview for pipeline-provenance consistency with the other phase-3 drills + independent vetting.

## Brain claim (PINNED)
Feature-based thematic fit / selectional preference GENERALISES to genuinely UNSEEN verb-argument pairs
(McRae et al. 1997/1998 thematic fit; Erk & Pado 2010 exemplar-based selectional preference): a human
rates a novel argument's fit from its FEATURES, not from having heard the exact pair. Word-identity
co-occurrence counting CANNOT -- on a truly unseen (zero-count) pair its PPMI is exactly 0, so it backs
off to chance. So the brain's advantage must show specifically on unseen / data-starved pairs (and
reverse where counting has data -- the crossover IS the signature). The prior drill
exp_exemplar_selpref_v1 (MIDDLE_BAND) tested only the DATA-RICH 15M regime where counting wins, with a
12-dim Lancaster space that was too thin -- this drills the correct regime with the richer 65-dim
predicted-Binder space.

## Regime + arms (one variable = how an unseen pair is scored; 2AFC, chance 0.5)
Gold = a constructed 2AFC on VERIFIED zero-count held-out pairs: for each verb hold its top feature-
covered filler entirely out of training counts (co-occurrence asserted == 0, verified not inferred),
pair it against a FREQUENCY-MATCHED filler never attested with that verb, score whether each arm ranks
the true filler above the distractor. Swept over 1M / 2M / 15M token budgets to expose the crossover.
- FEAT_GEN_BINDER65 [treatment] = exemplar/soft-max feature generalisation over the 65-dim predicted-Binder argument space.
- FEAT_GEN_LANC12 [treatment, richness ablation] = same over the thin 12-dim Lancaster space.
- WORDID_COUNT [FLOOR] = word-identity verb-argument PPMI (backs off to 0 on unseen pairs).
- FEAT_SHUFFLE [INFO-FREE TWIN] = FEAT_GEN with argument-feature rows shuffled across words. MUST LOSE.
- RANDOM [FLOOR] = matched-dim random argument vectors. MUST LOSE.
- CENTROID_BINDER65 [pooling ablation] = mean-first pooling (the Q2 over-compression) -- exemplar must beat it.

## Compute / remote-safety
remote_cpu_queue (numpy/scipy/sklearn ONLY -- NO torch: the cell deliberately reimplements the exemplar
similarity algebra locally to avoid hdlab.grounded_similarity's transitive torch import). Loads the 15M
PRE-PARSED cache; NEVER parses (grep-clean of spaCy on the run-time path; parse_and_cache never called;
fails loud if the cache is missing). Reuse of exp_exemplar_selpref_v1 / exp_binder_attr_prediction_
grounding_v1 / exp_structured_context_learner_v1 / exp_learn_from_reading_strong_arm_v1 is READ-ONLY.
The 65-dim predicted-Binder feature space is RE-FIT INTERNALLY from the raw Lancaster+Brysbaert+Binder
inputs (all 5 KB_REFERENTs already shipped for the Binder drill) -- no separate vector artifact needed.
bare == FULL (line 1052: `smoke = bool(args.smoke) or (args.mode == "smoke")`; the remote runner passes
no --mode). --self-test (incl. a POSITIVE CONTROL that the zero-count construction actually has zero
training co-occurrence on the real PPMI pipeline) + --smoke GREEN. metrics.json written INCREMENTALLY
per-arm (partial:true / arms_done; atomic tmp+os.replace; mode-keyed _ckpt dir). Local full-N preview
(1M/2M/15M, 4m41s) already read HARD_PASS with the crossover stark (unseen delta +0.38, seen -0.003) --
timeout 5400 is generous headroom.

## Results
data/exp_selpref_unseen_lowdata_v1/metrics.json (per-budget 2AFC accuracy per arm, paired deltas + CIs,
gate booleans, richness + pooling ablations, verified zero-count construction counts), synced back
~20 min. NOTE the standing infra gotchas: hd_metrics_sync is DISABLED (pull manually via the
orchestrator) and the runner writes a double-prefixed data/exp_exp_<name>/ path (SH-4). Strategy does
NOT integrate -- WIP until owner_verdict: DONE; to be VETTED (independent recompute) before folding into
SOLVED.md as a WIN.
