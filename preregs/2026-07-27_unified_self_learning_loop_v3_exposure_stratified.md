# Pre-registration: unified_self_learning_loop_v3 (exposure-stratified: does reading teach NEW concepts?)

Anchor: `unified_self_learning_loop_v3`
Cell: `experiments/exp_unified_self_learning_loop_v3.py`
Date: 2026-07-27
Author: exp_dev (hdi_exp_dev)
Status: SELF-TEST=PASS; SMOKE=PASS (tiny fresh encoder, mechanism + stratification gate); FULL pending GPU dispatch.

## Question (WHAT)
v2 (MIDDLE_BAND) validated the loop MECHANISM (sleep every cycle, comprehension real, controls clean,
retention held) BUT reading added NO SUSTAINED gain on the AGGREGATE held-out set. Likely cause: v2's
held-out concepts were pretraining-SATURATED (median ~655 ARC mentions) -- the encoder already KNEW them,
nothing to learn. The brain learns from NOVELTY. v3 asks the CORRECT question: on concepts the encoder
does NOT already know well (LOW pretraining exposure), does reading produce a SUSTAINED capability gain?

## Design (REUSE v2 loop machinery verbatim; add EXPOSURE-STRATIFIED per-slice AUC)
Imports `experiments.exp_unified_self_learning_loop_v2` (LOOP2) for the encoder/comprehension engine,
clarify FLAG, precision-weighted KALMAN consolidation + coverage-aware OVERRIDE gate, MDL-gated SLEEP,
the 3 loop-integrity controls, and `experiments.exp_scale_meaning_learn_arc_heldout_v2` (V2) for the
VET-confirmed leak-proof `relational_eval` probe. ONE addition: exposure stratification + per-slice AUC.

STRATIFICATION (the v3 core): well-covered held concepts are split into TERCILES by ARC mention count
`counts[ci]` (the pretraining-exposure proxy): LOW (bottom, under-known) / MID / HIGH (top, v2-saturated)
+ ALL (= reproduces v2 aggregate). Per-slice AUC is computed by calling V2.relational_eval with a
SUB-SPLIT whose `held_idx` is restricted to the slice, SHARING the same `train_eval_idx` negative pool.
Reading is HELD CONSTANT across concepts (every held concept reads the SAME mentions/cycle); the only
variable across slices is PRETRAINING EXPOSURE -> a clean IV.

CONSOLIDATION ABLATION (task item 3; NO common-mode / NO ca3):
- `plain`     : v1/v2 running mean over accumulated mention reps (baseline; reproduces wash-out).
- `precision` : precision-weighted KALMAN fold (K_t = p_mention/(prec_concept+p_mention); step SHRINKS
  as concept precision grows; outlier mentions down-weighted by LOCAL leave-one-out sibling reliability)
  + coverage-aware OVERRIDE gate (new read-knowledge overrides an established rep ONLY when high-
  confidence/high-coverage; else DEFER = retention). This is the best-motivated v2 brain-faithful arm.

ARMS (5): MAIN_plainavg | MAIN_precision | NO_READ (frozen) | SCRAMBLED (word-shuffled prose + sleep,
mode=precision) | READ_NO_SLEEP (episodic-only, mode=precision).

READING SCHEDULE (the lever that lets LOW-exposure concepts qualify): FULL n_cycles=5,
mentions_per_cycle=4 => need=20 (== min_mentions_eval), so concepts with as few as ~20 ARC mentions
enter the held set and every concept reads exactly 20 mentions (reading MATCHED across slices).

## Compute architecture
Storage strategy: SHARDED (per-concept rep store). Class: (c) mixed. Encoder forward = batched matmul
(GPU at FULL, loads the v2 d=512/6L checkpoint); loop/consolidation/Kalman + per-slice relational_eval =
light CPU/numpy. Per-slice probe = 4 slices x 5 arms x 5 cycles = 100 relational_eval calls over ~250
held queries each -- cheap numpy cosine, no training. -> overnight_queue (GPU).

## Bands (envelope-fail-bands)
### SMOKE (tiny fresh encoder; validates MECHANISM + STRATIFICATION only)
The across-cycle capability GAIN on real concepts is FULL-DEFERRED by ANALYTICAL JUSTIFICATION
(DISCRIMINATOR-SURVIVES-SCALE path B): a 0.53M/250-step encoder is below the signal threshold where
mention reps concentrate (v1/v2 MEASURED negative gain on tiny; V2 proved the text-rep carries
relational signal only at scale). The NEW machinery that DOES fire on tiny = the exposure-stratified
probe (per-slice AUC + monotone exposure ranges + per-slice query power).
- SMOKE_MECHANISM_PASS iff: 5 arms run end-to-end AND sleep EXECUTES every cycle for sleep-enabled arms
  (n_evaluated>=1) AND stratified_probe_fires (exposure LOW-median < HIGH-median AND >=2 slices with
  n_query>=8) AND LOW-slice power (n_query>=8) AND comprehension_fires (precision LOW > SCRAMBLED LOW at
  cycle-0 AND final) AND NO_READ LOW-slice frozen AND clarify fired AND plain vs precision stores DISTINCT.
- per-slice gain_on_tiny reported, NOT gated (expected noisy/negative on tiny).

### FULL (v2 checkpoint = comprehension engine) -- the real HARD-PASS
- HARD_PASS iff: MAIN_precision on the LOW slice SUSTAINS gain (AUC[final]-AUC[0] > +0.02 AND final
  within WASHOUT_EPS=0.01 of the LOW peak = no wash-out) AND LOW gain EXCEEDS HIGH gain (reading teaches
  the NEW concept more than the saturated one) AND LOW retention_ok (never drops below AUC[0]-0.02) AND
  sleep every cycle AND controls_below_main (best MAIN LOW-final > each control LOW-final) AND
  comprehension_fires AND LOW-slice power (n_query>=40) AND stratified_probe_fires.
  => teaches_new_concepts=True: the substrate LEARNS NEW concepts from reading.
- MIDDLE_BAND: LOW MAIN_precision gain > 0 but does not clear the sustained bar / misses a gate.
- HARD_FAIL: LOW MAIN_precision gain <= 0 (reading does NOT teach even novel concepts by encoder-
  averaging) -> route to loop-v4 (FAST EPISODIC store; sparse/pattern-separated, consolidate to encoder
  only over many exposures; measure on the fast store + a specific-fact-acquired probe). See
  notes/research_fast_concept_learning_informs_selflearning_loop_2026-07-27.md.

DEFLATE (mandatory on any null): report per-slice power (LOW n_query), reading amount (20 mentions/
concept, 4/cycle x 5), LOW/HIGH gain magnitudes, and plain-vs-precision LOW gains -> the why-autopsy
(few-shot capacity? metric sensitivity? amount of reading?) that points loop-v4.

## MEASURED (self-test + smoke, tiny fresh encoder)
- SELF-TEST=PASS (all real objects at N~tiny):
  MEASURED@self_test stdout: stratify LOW/MID/HIGH/ALL=3/3/3/9 (monotone exposure); encode reps
  L2-normalized; consolidation coherent_coh=0.9993 clarify_flag=1 lowcov_deferred=True (override gate +
  retention); per_slice_probe LOW/MID/HIGH=2/2/2 ALL=6 (partition-sum == ALL, leak-proof queries);
  ckpt_roundtrip reload_ok d_model=16.
- SMOKE verdict: SMOKE_MECHANISM_PASS
  MEASURED@data/exp_unified_self_learning_loop_v3_smoke/metrics.json:verdict
- sleep_fired_every_cycle=True; comprehension_fires=True; noread_low_flat=True; clarify_fired=True;
  modes_differ=True; power_ok=True (LOW n_query=20); stratified_probe_fires=True; exposure_ordered=True;
  slices_with_power=3.
- exposure stratification MEASURED@metrics.json:slice_meta -- LOW n=83 exposure[min/median/max]=12/17/24;
  HIGH n=84 exposure[min/median/max]=72/132/42620 (clean LOW-vs-HIGH separation; FULL 10M-line corpus
  will push HIGH-median into the saturated ~hundreds regime and keep LOW-median ~20-40).
- per-slice gain_on_tiny (deferred, NOT gated): LOW=-0.0103(wash=True) HIGH=+0.0791; plain LOW=-0.0103
  plain HIGH=+0.0788 -- noisy on tiny (below signal threshold), FULL-deferred per path B.

## SCHEMA-VET fields
- final_metrics_atomicity: tmp_replace (os.replace)
- arms_differ_verified: True (store fingerprints; plain vs precision DISTINCT MEASURED 4060b501 vs
  5ac1f74a); arms_differ_exempted: [(NO_READ, READ_NO_SLEEP)] rationale: both freeze the consolidated
  store at cycle-0 (same mode=precision) by construction -- read-off/sleep-off => reading changes nothing.
- cardinality_ok: n/a (fixed 5 arms x n_cycles; no seed/param sweep axis). cell_chunked: False (single seed).
- start_marker_written: True; crash_diagnostic_present: True; heartbeat_present: True
- defensive_error_checking: passed_all_4_patterns
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-verified clean)
- deterministic_seeding: True (stable sort with concept-id tiebreak for slices; fixed ints +
  np.random.default_rng(seed+...); no hash()/list(set()) ordering)
- discriminator_reachability: True. SMOKE discriminator (stratified-probe-fires + comprehension gap)
  MEASURED at smoke. FULL discriminator (LOW-slice sustained gain) is CAN-FAIL: if LOW is also flat it
  HARD_FAILs -> loop-v4; NOT by-construction (reading a low-exposure concept could still wash out; the
  precision+override arm is the mechanism under test, plain is the control).
- baseline_in_band: True (per-slice AUC 0.44-0.62 at smoke, not saturated, not floor)
- crlb_n/a: relational AUC has no closed-form noise floor for this regime; power gated via per-slice n_query.
- calibration_check: default_ok_for_this_regime (ClarifyGate banked thresholds; MDL cr=1.0; consolidation
  params inherited from v2's consol_cfg, principled not tuned-for-PASS; reading schedule chosen to admit
  LOW-exposure concepts, not to hit a band).
- effective_vs_nominal_parameter_audit: swept axis = exposure slice (LOW/MID/HIGH). EFFECTIVE param =
  ARC mention count per concept; reading is MATCHED (20 mentions) across slices so exposure is the ONLY
  IV. ALIGNED.
- bracket_includes_discriminating_band: per-slice AUC lands 0.44-0.62 at smoke (in [0.30,0.70]); FULL
  base AUC ~0.55-0.64 per v2 -> discriminating band populated.
- reproduce_prior_chain_grade_result_as_positive_control: ALL slice = v2 aggregate curve (reproduces v2
  at the test regime by construction; the v2 relational_eval probe is reused byte-for-byte).
- real_code_path_exercised: [V2.TinyTransformer, LOOP2._encode_sentences, LOOP2._concept_learn_result +
  per_cluster_gate, LOOP2._clarify_flag_population, LOOP2._kalman_fold, LOOP2._sleep_consolidate(override),
  ClarifyGate, _build_slices, _probe_stratified -> V2.relational_eval, LOOP2._build_encoder_from_ckpt]
  (all in self_test at N~tiny; ckpt round-trip).
- substrate_signature_checked: V2.TinyTransformer + V2.relational_eval + LOOP2 helpers bound via real
  calls in self_test.
- progress_logging: print_flush_true (per-arm per-cycle per-slice line; heartbeat.jsonl)
- HP_SCOPE: {MAIN_precision: [LOW_sustained_gain, LOW>HIGH_contrast, LOW_retention, comprehension,
  controls_below]; MAIN_plainavg: [LOW baseline control]; NO_READ/SCRAMBLED/READ_NO_SLEEP: [below-main
  on LOW, comprehension-negative for SCRAMBLED]}

## Invariants
TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX (symbolic gates + precision
Kalman + coverage override; no external LLM / no autograd at inference); LEAK-PROOF (predicted edge
disjoint from read text; per-slice probe reuses V2's degree-matched adjacency-excluded negatives). REAL
prose (ARC corpus). Store LOCAL-ONLY + UNCOMMITTED; NO canonical bank; NO push.

## VET flags (for skunkworks landed-VET)
1. Per-slice n_query: on FULL the LOW slice may have FEWER graph neighbours (low-exposure concepts are
   sparser in the adjacency graph) -> VET LOW n_query >= 40 power floor actually met at FULL; if not, the
   LOW verdict is under-powered (report, do not over-claim).
2. Sub-split reuse: per-slice AUC restricts held_idx but shares train_eval_idx. VET that restricting
   held_idx does not change the negative pool or leak (it does not: negatives are drawn from
   train_eval_idx, independent of which held concepts are queried).
3. teaches_new HARD_PASS requires LOW>HIGH contrast: VET this is a genuine novelty effect, not a LOW-slice
   base-AUC artifact (LOW starts lower so has more headroom). Report LOW/HIGH AUC[0] and gains separately.

## FULL invocation (orchestrator runs on GPU)
```
.venv/Scripts/python.exe experiments/exp_unified_self_learning_loop_v3.py --full \
  --ckpt data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt --seed 7
```
Metrics -> data/exp_unified_self_learning_loop_v3/metrics.json
queue: overnight_queue (GPU); timeout 10800s (3h, generous headroom; base encoding of all foundation
concepts at d=512/6L is matmul-heavy; 5 arms x 5 cycles + 100 cheap per-slice probes). Sibling modules
(exp_unified_self_learning_loop_v2, exp_scale_meaning_learn_arc_heldout_v2) auto-SCP via queue_add.sh
Pattern 6 (ast import-parse); orchestrator must confirm BOTH land on remote + push origin/main.
