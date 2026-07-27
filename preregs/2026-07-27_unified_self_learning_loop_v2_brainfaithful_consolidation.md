# Pre-registration: unified_self_learning_loop_v2 (brain-faithful consolidation)

Anchor: `unified_self_learning_loop_v2`
Cell: `experiments/exp_unified_self_learning_loop_v2.py`
Date: 2026-07-27
Author: exp_dev (hdi_exp_dev)
Status: SELF-TEST=PASS; SMOKE=PASS (tiny fresh encoder, mechanism gate); FULL pending GPU dispatch.

## Question (WHAT)
v1 (MIDDLE_BAND) validated the loop MECHANISM but knowledge_gain WASHED OUT: main_curve 0.636 ->
0.641 (cycle2) -> 0.638 (net +0.002, need +0.02) -- the plain-averaging DILUTION signature (early
reads help, then a uniform running mean regresses every concept toward the shared cross-concept
centroid = anisotropy/representation-degeneration). Does a BRAIN-FAITHFUL consolidation UPDATE produce
SUSTAINED knowledge_gain across cycles (gain > +0.02, no wash-out) while keeping sleep-every-cycle +
controls-below-main + retention + comprehension + leak-proof?

## Design (SWAP only the consolidation update + add override gate; reuse v1 machinery verbatim)
Imports v1's parent `experiments.exp_scale_meaning_learn_arc_heldout_v2` (V2) for ALL data-prep, the
encoder (TinyTransformer comprehension engine + tokenizer), and the VET-confirmed leak-proof
`relational_eval` probe. Reuses v1's clarify FLAG, hippocampal FAST-WRITE, MDL-gated SLEEP commit, the
3 loop-integrity controls, and the leak-proof probe. Changes ONLY the consolidation update rule.

CONSOLIDATION ABLATION (cumulative; 4 MAIN mode-arms):
- `plain`        : v1 exact -- running mean over all accumulated mention reps (MUST reproduce wash-out).
- `precision`    : + precision-weighted KALMAN fold. Innovation gain K_t = p_mention/(prec_concept +
  p_mention) (CORRECT Bayesian form; the drill's row-1 K was inverted -- corrected). Step SHRINKS as
  concept precision grows; outlier mentions down-weighted by LOCAL leave-one-out sibling reliability
  (per drill: precision MUST be local, never a global statistic). + coverage-aware OVERRIDE GATE.
- `precision_cm` : + COMMON-MODE SUBTRACTION (all-but-the-top, Mu-Viswanath 2018): strip mu + top-`cm_rank`
  shared directions (fit ONCE from the FIXED foundation reps) from each mention BEFORE the Kalman fold,
  and from the base rep matrix used in the probe (both sides of the cosine in the same de-anisotropized
  space). Fixes centroid-regression (a coherent BIAS precision-weighting alone cannot remove).
- `ca3`          : + CA3-COMPLETION-before-write (scour note HARD_PASS mechanism): denoise the
  consolidated readout toward the clean foundation-rep manifold via a soft k-NN attractor step BEFORE
  commit. Uses ONLY text-derived foundation reps; BLIND to the answer graph -> leak-proof preserved.

COVERAGE-AWARE OVERRIDE GATE (brain-faithful modes; scour note's #1 risk = knowledge-override net-hurt):
new read-knowledge overrides an established rep ONLY when high-confidence/high-coverage
(new_conf = ((coh+1)/2)*min(1, n_mentions/override_cov_target) >= override_min AND >= prev_conf -
override_defer_eps); else DEFER to the existing rep (= retention). `plain` keeps v1's gate exactly.

Controls (loop-integrity, run at mode=precision_cm): NO_READ (frozen) | SCRAMBLED (word-shuffled prose
+ sleep) | READ_NO_SLEEP (episodic-only). 7 arms total.

## Compute architecture
Storage strategy: SHARDED (per-concept rep store). Class: (c) mixed. Encoder forward = batched matmul
(GPU at FULL); loop/consolidation/common-mode-SVD/CA3-kNN = light CPU/numpy. FULL loads the v2 GPU
checkpoint -> overnight_queue (GPU). Common-mode SVD is on the fixed foundation (few-thousand x 512),
done once.

## Bands (envelope-fail-bands)
### SMOKE (tiny fresh encoder; validates the MECHANISM only)
The across-cycle capability GAIN is FULL-DEFERRED by ANALYTICAL JUSTIFICATION (DISCRIMINATOR-SURVIVES-
SCALE path B): a 0.53M/250-step encoder is below the signal threshold where mention reps concentrate
(v1 MEASURED negative gain on tiny; V2 proved the text-rep carries relational signal only at scale).
The NEW-mechanism discriminator that DOES fire on a tiny encoder = COMMON-MODE removal reduces
cross-concept anisotropy (the fix's load-bearing effect).
- SMOKE_MECHANISM_PASS iff: 7 arms run end-to-end AND sleep EXECUTES every cycle (n_evaluated>=1) AND
  relational power (n_query>=15) AND clarify fired AND NO_READ frozen AND comprehension_fires
  (precision_cm MAIN > SCRAMBLED at cycle-0 AND final) AND 4 modes produce DISTINCT stores AND
  cm_reduces_anisotropy (precision_cm final cross-concept sim < plain final - 0.002).
- per-mode gain_on_tiny reported, NOT gated (expected negative on tiny).

### FULL (v2 checkpoint = comprehension engine) -- the real HARD-PASS
- HARD_PASS iff: a brain-faithful arm (precision / precision_cm / ca3) SUSTAINS gain (AUC[final]-AUC[0]
  > +0.02 AND final within WASHOUT_EPS=0.01 of the arm's peak = no wash-out) AND its gain BEATS plain's
  AND plain REPRODUCES the wash-out (plain not sustained -> validates the anisotropy diagnosis) AND
  sleep executes every cycle AND controls_below_main (best MAIN final > each control final) AND
  comprehension_fires AND power (n_query>=40) AND the winning arm's retention_ok (never drops below
  AUC[0]-0.02).
- MIDDLE_BAND: some brain-faithful arm gain > 0 but no arm clears the sustained bar / misses a gate.
- HARD_FAIL: no brain-faithful arm shows positive gain (the update swap does not fix the wash-out) ->
  route to mechanism iteration (exemplar/multi-sense consolidation, or component-selective whitening).

## MEASURED (self-test + smoke, tiny fresh encoder)
- SELF-TEST=PASS (all real objects at N~tiny):
  MEASURED@self_test stdout: common_mode sim 0.702->-0.051; kalman step_cold 0.651 vs step_confident
  0.0238; prec_clean 3.999 vs prec_noisy 1.994; ca3 sim 0.579->0.934; override defers low-coverage
  (n_consol=0, rep unchanged); ckpt round-trip reproduces reps.
- SMOKE verdict: SMOKE_MECHANISM_PASS
  MEASURED@data/exp_unified_self_learning_loop_v2_smoke/metrics.json:verdict
- comprehension_gap_cycle0 = +0.0371 ; comprehension_gap_final = +0.0529 (comprehension_fires=True)
- cm_reduces_anisotropy=True: plain_xsim_final=1.000 (total anisotropic collapse) vs cm_xsim_final=0.045
- sleep_fired_every_cycle=True ; noread_flat=True ; clarify_fired=True ; modes_differ=True (4 distinct)
- power_ok=True ; n_query_final=73 ; n_held_concepts=250
- per-mode gain_on_tiny (deferred, NOT gated): plain=-0.0335(wash=True) precision=-0.0266
  precision_cm=-0.0386 ca3=-0.0725 ; winning_consolidation=None (expected on tiny)

## SCHEMA-VET fields
- final_metrics_atomicity: tmp_replace (os.replace)
- arms_differ_verified: True (held-rep store fingerprints; 4 MAIN modes distinct MEASURED);
  arms_differ_exempted: [(NO_READ, READ_NO_SLEEP)] rationale: both freeze the consolidated store at
  cycle-0 (same mode=precision_cm) by construction -- sleep-off/read-off => reading changes nothing.
- cardinality_ok: n/a (fixed 7 arms x n_cycles; no seed/param sweep axis). cell_chunked: False (single seed).
- start_marker_written: True ; crash_diagnostic_present: True ; heartbeat_present: True
- defensive_error_checking: passed_all_4_patterns
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-verified)
- deterministic_seeding: True (fixed ints + np.random.default_rng(seed+...); no hash()/list(set()) ordering)
- discriminator_reachability: True (comprehension gap +0.037 + cm anisotropy drop 1.0->0.045 MEASURED at smoke)
- baseline_in_band: True (AUC 0.48-0.58, not saturated, not floor)
- crlb_n/a: relational AUC has no closed-form noise floor for this regime; power gated via n_query.
- calibration_check: default_ok_for_this_regime (ClarifyGate banked M1.8 thresholds; MDL cr=1.0;
  consolidation params in consol_cfg, principled from drill + scour notes, not tuned-for-PASS)
- real_code_path_exercised: [TinyTransformer, _encode_sentences, _fit/_apply_common_mode, _kalman_fold,
  _mention_precision, _ca3_complete, _sleep_consolidate(override), _concept_learn_result+per_cluster_gate,
  ClarifyGate, V2.relational_eval, _build_encoder_from_ckpt] (all in self_test at N~tiny; ckpt round-trip)
- substrate_signature_checked: V2.TinyTransformer + relational_eval bound via real calls in self_test
- progress_logging: print_flush_true
- HP_SCOPE: {MAIN_precision/precision_cm/ca3: [sustained_gain, beats_plain, retention, comprehension];
  MAIN_plainavg: [must reproduce wash-out]; controls: [below-main, comprehension-negative for SCRAMBLED]}

## Invariants
TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX (symbolic gates + Kalman +
streaming-PCA common-mode + k-NN attractor; no external LLM / no autograd at inference); LEAK-PROOF
(predicted edge disjoint from read text; CA3 blind to adjacency graph). REAL prose (ARC corpus). Store
LOCAL-ONLY + UNCOMMITTED; NO canonical bank; NO push.

## VET flags (for skunkworks landed-VET)
1. CA3-completion pulls held reps toward text-derived foundation NN. This uses ONLY text reps (not the
   adjacency answer graph), so it does not break the structural leak-proof guarantee -- but VET should
   confirm CA3 does not inflate AUC on the SCRAMBLED control (SCRAMBLED runs precision_cm, not ca3; if
   ca3 wins, a SCRAMBLED_ca3 sanity arm may be warranted before banking).
2. cm_reduces_anisotropy is a mechanism-CORRECTNESS check (CM code removes shared variance), not the
   capability claim; the capability claim (sustained AUC gain) is FULL-only.
3. common-mode mu/U is fit from concept-MEAN reps (foundation) but applied to MENTION reps; VET the
   space-consistency assumption holds at FULL scale (same encoder => same anisotropy axis, expected).

## FULL invocation (Director/orchestrator runs on GPU)
```
.venv/Scripts/python.exe experiments/exp_unified_self_learning_loop_v2.py --full \
  --ckpt data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt --seed 7
```
Metrics -> data/exp_unified_self_learning_loop_v2/metrics.json
queue: overnight_queue (GPU); timeout 10800s (3h, generous headroom; base encoding of all concepts +
7 arms x 6 cycles at d=512/6L is matmul-heavy).
