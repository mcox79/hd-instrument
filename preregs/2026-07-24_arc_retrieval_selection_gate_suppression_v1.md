# Pre-reg: arc_retrieval_selection_gate_suppression_v1 (2026-07-24)

## Question (can-fail, judged ON THE ANSWER not recall)
The bind+settle combiner reaches Challenge 0.696 on CLEAN gold facts but DROWNS on the noisy
real spreading-activation pool (Challenge ~0.28-0.31). MEASURED@disk:
- combiner on gold: oracle_bundle_acc_challenge = 0.6961
  MEASURED@d:/AI/hd-instrument/data/exp_arc_aggregation_retriever_bindsettle_v1/metrics.json:oracle_bundle_acc_challenge
- combiner on noisy retrieved pool: retr_bundle_acc_challenge = 0.2834 (same file)
- spreading-pool baseline -> bundle end-to-end: Challenge 0.3101 (151/487)
  MEASURED@d:/AI/hd-instrument/data/exp_arc_retrieval_multicue_ppr_discriminative_v1/metrics.json:end_to_end.A.bundle.challenge

The brain never feeds a noisy pool to reasoning: Stage-5 RETRIEVAL CONTROL first (Badre & Wagner
anterior-VLPFC controlled/strategic retrieval + mid-VLPFC post-retrieval SELECTION + Anderson RIF
competitor suppression). We have NO selection gate. This cell tests whether inserting a SELECTION
GATE (goal-bias + competitor-suppression) BEFORE the UNCHANGED combiner beats the noisy-pool
baseline ON THE ANSWER, ESPECIALLY on the Challenge surface-lure subset.

Authoritative design: notes/research_brain_qa_architecture_completeness_2026-07-24.md (cheap decisive
test). Prior-work check (substrate_query "retrieval selection gate suppression competitor goal-bias
controlled retrieval ARC surface lure"): top hit generic "retrieval" cosine 0.3828; nothing on
selection-gate/suppression above 0.30 -> genuinely NOVEL, not a rediscovery.

## ONE variable = the selection gate (combiner + spreading pool UNCHANGED)
Pool source = the VALIDATED spreading-activation fact scores (PPR arm B), imported UNCHANGED from
exp_arc_retrieval_multicue_ppr_discriminative_v1. Top-K_POOL facts = the noisy pool. All arms consume
the IDENTICAL pool; they differ ONLY in the selection step before the UNCHANGED agg.aggregate(bundle).

- gate_score(f) = goal_score(f) - MU * lure_penalty(f)
  - goal_score(f) = relu(cos(f, STEM)) + LAMBDA_DISC * (max_c cos(f,choice_c) - 2nd_max_c)  [goal-bias:
    relevance to the question-goal AND choice-separating; NOT stem-cosine alone]
  - lure_penalty(f) = surf_pull(f) * lure_align(f)  [RIF competitor-suppression]
    - surf_pull(f) = Jaccard(fact content-words, stem content-words)  (retrieved-by-surface signal)
    - lure_align(f) = 1 if argmax_c cos(f,choice_c) is the STANDOUT surface-lure choice else 0
    - standout surface-lure choice = the UNIQUE argmax of stem-word-overlap among choices, strictly
      above the mean overlap (answer-agnostic; the "designed trap" distractor). NEVER uses the gold.

## Arms (all sourced from the SAME spreading pool; combiner UNCHANGED = bundle)
- A_noisy  : all K_POOL pool facts -> combiner            [BASELINE = current noisy pool]
- B_gate   : top-K_SEL by gate_score -> combiner          [MECHANISM: goal-bias + suppression]
- S_nosupp : top-K_SEL by goal_score alone (MU=0) -> combiner   [ABLATION: suppression OFF]
- R_random : K_SEL random pool facts -> combiner          [MUST-FAIL control: "fewer facts" driver]
- ref_oracle_gold : gold central facts -> combiner        [CONTEXT ceiling ~0.696; not in discriminator]

## Metrics + bands (PRIMARY = END-TO-END ARC accuracy; NOT recall)
Splits: Easy, Challenge, Challenge-LURE, Challenge-NONLURE.
LURE subset (eval stratification, may use gold) = Challenge questions where a distractor's stem-word
content-overlap STRICTLY exceeds the correct answer's overlap (the surface-trap the set is built on;
matches agg-cell miss_diagnosis). The GATE never uses gold; the subset partition does (eval only).

HARD-PASS (all four):
1. B_gate Challenge-LURE acc - A_noisy Challenge-LURE acc >= HP_LURE_LIFT = 0.08 (notes pre-reg)
2. McNemar (A_noisy vs B_gate on LURE subset) p < 0.05
3. Selectivity: |B_gate - A_noisy| on Challenge-NONLURE <= 0.05 (targets the diagnosed failure mode,
   not a general lift that would signal leakage/confound)
4. RANDOM control does NOT help: (R_random LURE - A_noisy LURE) <= RANDOM_MAX = 0.03
   AND suppression load-bearing: (B_gate LURE - S_nosupp LURE) >= HP_SUPP = 0.02

MIDDLE_BAND: LURE lift in [MB_LURE_LIFT=0.03, 0.08) OR HP met but McNemar not significant OR
suppression/random gates unmet.

HARD-FAIL: LURE lift < 0.03 (selection does not beat the noisy-pool baseline on the answer)
  -> then the COMBINER itself (not the pool) is the wall; report straight.
DISQUALIFY (per notes anti-precision guard): if suppression fires on the CORRECT choice MORE than the
WRONG choice across the LURE subset -> crude oppose-signal disqualified (report; do not re-tune).

## SCHEMA-VET / cell-template
- baseline_in_band: A_noisy challenge ~0.28 in (0.05, 0.95) -> in band. AG-guard: A_noisy < 0.95.
- discriminator-fires: on LURE subset, sum(n_lure_facts_in_pool) > 0 AND B_gate selection differs
  from S_nosupp selection for >=1 question (suppression actually removes facts). Asserted at smoke.
- DISCRIMINATOR-SURVIVES-SCALE: smoke runs the FULL graph (all ~9720 facts -> real pool); question
  SUBSET only. The pool + gate fire at real graph scale.
- arms_differ: A/B/S/R pick-digests distinct (arms-differ hash).
- final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat.
- except SystemExit: raise BEFORE except Exception (no BaseException; no bare except).
- deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()/list(set()).
- crlb_n/a: end-to-end accuracy discriminator (no closed-form noise floor); band feasibility set by
  the measured 0.28 baseline vs 0.696 ceiling (>=0.08 lift is well inside the 0.41 headroom).
- storage_strategy = sharded (each fact = own embedding + own graph node; no superposition).
- calibration_check: default_ok_for_this_regime (gate hyperparams author-set a priori; NOT tuned to
  force a win; if HARD-FAIL, report the combiner is the next wall, do not re-tune thresholds).
- progress_logging: line_buffered_stdout (full wall ~2-3 min < 30 min; heartbeat per stage anyway).
- HYPOTHESIZED vs MEASURED: baseline 0.31 / 0.283 and ceiling 0.696 are MEASURED@disk (above);
  the +0.08 target is HYPOTHESIZED@this prereg (notes pre-reg), verified by the run.

## Hyperparams (author-designed a priori)
N_DIM=2048, K_POOL=20, K_SEL=4 (Cowan-4 / WorldTree ~2.5 central), LAMBDA_DISC=1.0, MU_SUPP=1.0,
HOPS=2, DAMP=0.5, SEED_COS=0.60, MIN_TERM_LEN=4 (reused from the PPR cell, unchanged).

## Contract
INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-portable);
NO push/remote-persist; ASCII-only; repo .venv; agent-reported VET-PENDING.
