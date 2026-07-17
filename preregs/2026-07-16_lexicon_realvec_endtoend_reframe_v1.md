# Pre-reg: lexicon_realvec_endtoend_reframe_v1

Filed BEFORE full dispatch. ASCII-only. Local numpy + torch-CPU (fit cached). No queue/GPU/atoms/push.

## Question (culmination + reframe resolution)
Two questions, ONE cell, SHARED real DC-centered CoDEx geometry:
- Q1 END-TO-END: does the whole glass-box-reading pipeline (LEARN lexicon [VET'd cross-situational
  rule] -> proven SVO role-filler scaffold -> BIND/UNBIND -> GROUND against REAL CoDEx concept
  geometry with the DC-CENTERING encoding fix) work when the concept codebook is the REAL fitted
  CoDEx vectors (DC_DEFLATE-lifted) rather than benign i.i.d. phasors? Attribution: does LEARNED
  grounding track ORACLE-lexicon grounding on the SAME real geometry (learning rule survives real
  geometry)?
- Q2 REFRAME: is the real-negatives-gate residual (negrej ~0.8, not 1.0) the genuine COST OF REAL
  GROUNDING (surviving negatives are SEMANTICALLY near-true) or a fixable ARTIFACT?

## Critical framing (do NOT repeat the vacuous-1.0 trap)
negrej=1.0 is the RANDOM ceiling BECAUSE random codes have no semantic neighbours; a genuinely
grounded codebook is EXPECTED below 1.0. So the bar is NOT negrej->1.0. Q1 bar = LEARNED tracks
ORACLE on the SAME real geometry. Q2 bar = survivors demonstrably semantic AND geometry-driven.

## Arms (contract, fixed)
- Q1: LEARNED_real / ORACLE_real (attribution upper bound) / RANDOM (floor) / LEARNED_benign
  (reference = marginal geometry cost).
- Q2: DC_DEFLATE (primary, geometry-preserving) / FPE_WIDE (geometry-discarding control) / RANDOM
  (floor / framing). Plus a permutation test on the survivor/rejected near-true labels.

## Encoding
DC_DEFLATE (encoding_fix_v1): FPE at target-median-coherence bandwidth + glass-box kernel-centering
(remove the all-positive-RBF common-mode). Geometry-preserving (concept_geomPres > 0.20 asserted in
self-test) -- the standard lift the task specifies.

## Reframe statistic (Q2, decisive)
For each real negative (s,r,o'): near_true = max over true objects to of raw-embedding cos(Xn[o'],
Xn[to]) (RAW k-dim X, independent of the lift). Split negatives at the @90%-recall gate threshold
(10th pctile of positive resonance) into SURVIVORS (>=thr) vs REJECTED (<thr). Statistic:
sep-AUC = P(survivor near_true > rejected near_true), with a one-sided permutation p-value
(exchangeable survivor/rejected labels). Anti-tautology: geometry-DISCARDING codebooks must NOT
retain a semantic-survivor population (survivor-population contrast, encoding_fix-consistent: geometry
and survivors are coupled -- ungrounded => ~no survivors, not non-semantic survivors).

## Pre-reg bands (envelope-fail)
- HARD-PASS: (Q1) gap_real = ORACLE_real_obj - LEARNED_real_obj <= 0.15 AND LEARNED_real grounds
  >= RANDOM + 0.30; AND (Q2) DC_DEFLATE sep-AUC >= 0.58 with perm_p < 0.01 AND geometry-driven
  (DC survivor population >= 50 AND both discarding controls collapse it by >= half).
- HARD-FAIL: (Q1) gap_real > 0.30 OR LEARNED_real - RANDOM < 0.05 [rule does NOT survive real
  geometry]; OR (Q2) DC_DEFLATE sep-AUC < 0.53 OR perm_p >= 0.05 [residual is an unfixed artifact].
- MIDDLE otherwise (partial recovery; do NOT over-read as end-to-end success).

## Compute architecture
Sequential-CPU, justified: cell IS the glass-box FHRR reference + reuses a small cached real KGE fit
(fit_kge_anchor1, e200 seed=1 cached npz). No GPU speedup axis (V<=200 learner + one loop over 1862
negatives + 2000-perm test). Wall < 1 min full (fit cached). Storage: per-subject bundle (single-hop
relation-keyed unbind) -> bundled correct. Run to completion INLINE (local); no queue dispatch.

## SCHEMA-VET fields
- arms_differ_verified: true (hash over real vs benign concept codebooks + DC vs random loop codebooks)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise before except Exception (no BaseException / bare except): verified
- crlb_n/a: "grounded-retrieval + rank-based sep-AUC; no single closed-form noise floor. ORACLE_real
  reachable ~1.0 (3-term bundle SNR high); RANDOM Q1 at chance 1/V_noun; negrej band empirical."
- baseline_in_band: RANDOM Q1 ~chance (0.005); RANDOM Q2 negrej ~1.0 (floor); ORACLE_real in (0.3,1.0)
- discriminator_survives_scale: full N=2048 / V=200; FPE_WIDE geomPres ~0 control present; sep-AUC
  telemetry-sensitive (survivors >> rejected near-true; random => 0 survivors)
- deterministic seeding: fixed int seeds, sorted() vocab, no hash()/list(set())
- real_code_path: self-test constructs the REAL fitter (fit_kge_anchor1) AND the REAL learner
  (learn_lexicon via track_a_eval) at tiny scale
- calibration_check: default_ok_for_this_regime (reuses VET'd learner + loop + DC_DEFLATE unchanged)
- cell_chunked: false (single-shot, wall < 1 min); start_marker_written: true; crash_diagnostic: true;
  heartbeat_present: false (reason: single-shot < 1 min inline run, start_marker + atomic metrics cover)
- defensive_error_checking: "start_marker + crash_metrics + atomic tmp_replace; heartbeat exempt (short)"

## Determinism nit fixed (task-authorized)
exp_lexicon_learned_grounding_scaled_v1.py:293 `list(scene_n | scene_v)` -> `sorted(...)`
(PYTHONHASHSEED-safe; the numeric result was already order-independent -- competitive-alignment sums
into a dict -- but the module's own discipline forbids list(set)).
