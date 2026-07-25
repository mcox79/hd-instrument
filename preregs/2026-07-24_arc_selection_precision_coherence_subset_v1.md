# Pre-reg: arc_selection_precision_coherence_subset_v1 (2026-07-24)

## Question (can-fail, judged ON THE ANSWER not recall)
The max-retrieval diagnostic (29543) PROVED reachability is SOLVED: the WIDE re-retrieval pool
(RR top-100) has recall@100 = 0.69 of the gold central facts and an ALL-REACHABLE ceiling of 1.0 --
the pool CONTAINS the gold facts. But a wide high-recall pool does NOT lift the answer. MEASURED@disk
(data/exp_arc_retrieval_max_recall_ksweep_reretrieval_v1/metrics.json):
- recall@100 (SC) = 0.6911  MEASURED@:recall_curve.SC.at100
- E_wide_gate Challenge (current gate on the wide pool) = 0.3306  MEASURED@:end_to_end.E_wide_gate.challenge
- E_narrow_gate Challenge = 0.3368  MEASURED@:end_to_end.E_narrow_gate.challenge (wide flat vs narrow)
- E_oracle Challenge (gold facts -> combiner) = 0.7125  MEASURED@:end_to_end.E_oracle.challenge

The gate+combiner picks a surface-LURE while an oracle handed the exact gold facts reaches 0.7125.
The pool CONTAINS the gold; SELECTION cannot ISOLATE it. The wall relocated from retrieval to
SELECTION-PRECISION. The ENTIRE remaining gap on Challenge (0.33 -> 0.71, ~0.38) is selection.

Brain grounding (DONE, no new drill): VLPFC post-retrieval SELECTION + relevance-gating + RIF
suppression (notes/research_brain_qa_architecture_completeness_2026-07-24.md); discriminative
relevance is relative to the answer-SET not stem-cosine (Badre-Wagner,
notes/research_arc_retrieval_biology_and_design_2026-07-24.md); COHERENCE = the gold facts cohere
into an explanation of ONE answer, distractors do not -- Kintsch construction-integration / Thagard
ECHO settle to find the COHERENT SUBSET.

Prior-work check (substrate_query "selection precision post-retrieval gating coherence subset
relevance discriminative fact selection ARC"): top hit generic "selection" WordNet concept cosine
0.3955; old backup-doc chunks (META_RULE_F) 0.35; basal-ganglia action-selection drill 0.34; NO
prior ARC selection-precision experiment cell above 0.30 -> genuinely NOVEL, not a rediscovery.
(META_RULE_F caution noted: retrieval-success-driven importance is magnitude-coupled by construction;
this cell's selection signals are answer-agnostic and NOT gated on retrieval success, so no leak.)

## ONE variable = the SELECTION SIGNAL (wide pool + combiner UNCHANGED)
Pool source = the VALIDATED WIDE re-retrieval pool (RR top-100), imported UNCHANGED from
exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 (mr.reformulate_seeds + mr._rownorm_scores over
the UNCHANGED PPR graph). Combiner = agg.aggregate('bundle'), imported UNCHANGED. All arms consume the
IDENTICAL wide pool + the IDENTICAL combiner; they differ ONLY in the selection step that picks
K_SEL=4 facts. ALL selection signals are ANSWER-AGNOSTIC (never see the correct index or the gold
uids); gold is used ONLY for the ORACLE arm and for evaluation.

Selection signals:
- REL  (relevance, goal-biased to the answer-SET): relu(cos f,STEM) + mean_c relu(cos f,choice_c).
  Relevance to the question topic INCLUDING any answer choice (not the separating margin).
- COH  (COHERENCE-SUBSET, the KEY hypothesis): Kintsch/ECHO settle (agg._relax, UNCHANGED settle
  math) over the SIGNED fact-fact coherence matrix FF=cos(f_i,f_j) (positive=consistent,
  negative=contradiction), seeded by the relevance af0. Select the facts with highest SETTLED
  activation = the subset that COHERES into one explanation. Coherent gold facts reinforce; incoherent
  lures lose share.
- DISC (discriminative): choice-separating margin max_c cos(f,choice_c) - 2nd_max_c. Facts that most
  separate ONE choice from the rest (answer-agnostic; judged on the ANSWER now, NOT recall -- the
  metric we earlier dropped this signal on was recall, the wrong metric).
- COMB (combined): min-max normed REL + COH + DISC - MU_SUPP * lure_penalty (RIF suppression of
  surface-lure-supporting facts; lure_penalty imported UNCHANGED from the gate).

## Arms (all: WIDE pool -> selection -> UNCHANGED bundle combiner; judged on the ANSWER)
- A_gate : current gate.gate_scores top-K_SEL -> combiner    [BASELINE = E_wide_gate analog ~0.33;
           POSITIVE CONTROL reproducing the prior gate at the test regime]
- REL / COH / DISC / COMB : the four selection signals            [MECHANISM arms]
- RND    : K_SEL random pool facts -> combiner               [MUST-FAIL control: "fewer facts" driver]
- ORACLE : gold central facts -> combiner                    [CEILING ~0.71; not in the discriminator]

## Metrics + bands (PRIMARY = END-TO-END ARC Challenge accuracy; NOT recall)
Splits: Easy, Challenge, Challenge-LURE. PRIMARY discriminator = Challenge (all), best selection arm
vs A_gate. gap = ORACLE Challenge - A_gate Challenge (~0.38).

HARD-PASS (all three):
1. best selection arm Challenge acc - A_gate Challenge acc >= HP_CHAL_LIFT = 0.05
   (>= ~13% of the ~0.38 gap = a MATERIAL fraction)
2. McNemar (A_gate vs best arm on Challenge) p < MCNEMAR_ALPHA = 0.05
3. RANDOM control does NOT help: (RND Challenge - A_gate Challenge) <= RANDOM_MAX = 0.02

MIDDLE_BAND: best-arm Challenge lift in [MB_CHAL_LIFT=0.02, 0.05) OR HP lift met but McNemar not
significant OR the random gate unmet. Selection helps but not decisively.

HARD-FAIL: best-arm Challenge lift < 0.02 (NO selection signal beats the current gate on the answer)
  -> selection-precision from a contains-gold pool is ITSELF the hard wall. Report straight; the
  redirect is DEEPER meaning/grounding for relevance (the relocated hypothesis), NOT more retrieval or
  a re-tuned surface gate. This is a real can-fail outcome -- the wide-pool gate already came in FLAT
  vs the narrow gate (0.3306 vs 0.3368), so beating A_gate by +0.05 is a genuine bar.

SATURATED (report, not a mechanism result): A_gate Challenge >= 0.95.

SECONDARY (diagnostic, NOT the verdict): selection-precision vs gold = fraction of each arm's selected
facts that are gold central facts (mean over Challenge questions). Does the winning signal actually
pick more gold? Gold used for EVAL only.

## SCHEMA-VET / cell-template
- baseline_in_band: A_gate challenge ~0.33 in (0.05, 0.95) -> in band. AG-guard: A_gate < 0.95.
- discriminator-fires: the planted coherence-subset self-test asserts COH recovers the coherent gold
  subset that REL drowns and the UNCHANGED combiner FLIPS the answer (COH picks correct, REL picks
  lure) -> the key mechanism is reachable and load-bearing. Verified at self-test (PASSED).
- DISCRIMINATOR-SURVIVES-SCALE: smoke runs the FULL graph (all ~9720 facts -> real wide pool at
  scale); question SUBSET only (150 Easy + 150 Challenge). The pool + all selection signals fire at
  real graph scale. FULL widens the question slice (500 Easy + 600 Challenge) for McNemar power.
- POSITIVE CONTROL AT TEST REGIME (Gate D): A_gate reproduces the current gate on the wide pool
  (E_wide_gate analog); if A_gate Challenge deviates materially from ~0.33 the pool/gate wiring is
  wrong and downstream arms are suspect.
- arms_differ: A_gate/REL/COH/DISC/COMB/RND pick-digests -> require >= 4 distinct (arms-differ hash).
- final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat.
- except SystemExit: raise BEFORE except Exception (no BaseException; no bare except). ASCII-only.
- deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()/list(set()).
- no gold leak: every selection signal is answer-agnostic (STEM, choices, fact-fact cos, surface-lure
  identification); the correct index + gold uids enter ONLY the ORACLE arm and the eval metrics.
- crlb_n/a: end-to-end accuracy discriminator (no closed-form noise floor); band feasibility set by
  the measured A_gate ~0.33 vs oracle ~0.71 (a +0.05 lift is well inside the ~0.38 headroom).
- storage_strategy = sharded (each fact = own embedding + own graph node; no superposition).
- calibration_check: default_ok_for_this_regime (selection hyperparams author-set a priori; wide pool
  + combiner UNCHANGED; NOT tuned to force a win; random-select present as must-fail; if HARD-FAIL,
  report the deeper-meaning redirect, do NOT re-tune thresholds).
- progress_logging: line_buffered_stdout (full wall target < 10 min; heartbeat per stage anyway).
- HYPOTHESIZED vs MEASURED: recall@100 0.69, A_gate/E_wide_gate 0.3306, oracle 0.7125 are
  MEASURED@disk (above); the +0.05 target is HYPOTHESIZED@this prereg, verified by the run.

## Hyperparams (author-designed a priori)
N_DIM=2048, K_WIDE=100 (UNCHANGED from max-recall), K_SEL=4 (Cowan-4 / WorldTree ~2.5 central),
RR_TOP_T=10 (UNCHANGED), MU_SUPP=1.0 (UNCHANGED from gate), SETTLE_T=50, SETTLE_EPS=1e-3 (UNCHANGED
Kintsch CI from the combiner), HOPS=2, DAMP=0.5, SEED_COS=0.60, MIN_TERM_LEN=4 (UNCHANGED from PPR).
SEED=20260726. FULL eval slice bounded (limit_easy=500, limit_chal=600) to fit one INLINE-LOCAL
foreground call (mirrors the max-recall FULL that ran in ~108s).

## Contract
INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-portable);
NO push/remote-persist; ASCII-only; repo .venv; agent-reported VET-PENDING.
