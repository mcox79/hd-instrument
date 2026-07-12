# Pre-reg: Decisive ROTATION-score reasoning cell (glass-box RotatE) on CSKG L2-genuine

Date: 2026-07-11. Author: exp_dev. Status: pre-registered BEFORE the run.

Cells:
- Core: `experiments/_course_c_rotate_core_v1.py`
- FULL (per-seed process isolation): `experiments/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_v1.py`
- GPU memory smoke (2-seed): `experiments/exp_course_c_rotate_cskg_l2_memsmoke_v1.py`

## Question
Does a ROTATION-score fit (RotatE-equivalent glass-box phase rotation = PP-275's validated FHRR-bind
primitive) beat the frequency incumbent (POP_RELFREQ) on held-out GENUINE-L2 composition edges of the CSKG
dense core, on the FAIR low+mid-degree stratum, degree-stratified, apples-to-apples on the pinned split? And
does ROTATION beat the ADDITIVE-TransE head-to-head (same recipe, additive score) -- i.e. does our glass-box
reproduce the field's RotatE > TransE result?

## Why now (diagnosis this corrects)
The prior decisive cell + the capacity ladder (`exp_course_c_oracle_capacity_ladder_v1` -> `LADDER_FIT_LIMITED`)
both used ADDITIVE-TransE scoring `s = gamma - ||X_h + D_r - X_t||` in ALL fit variants. Additive TransE is
provably disqualified for CSKG's two dominant relations (RotatE Table 1: TransE cannot model SYMMETRIC
relations = SYNONYM; TransH: cannot model 1-to-N = IS_A). The ladder's additive-anchor1 oracle (transductive,
sees the answers) topped out at direct hits@10 = 0.424 (k32/dim8192), fpe hits@10 = 0.000 -- fit-limited even
transductively, and the ell=0.55 FPE kernel fully underflowed. Per the decision tree's own escalation, this
licenses the FUNCTIONAL-FORM change (rotation) -- MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json:ladder.

## Core change (load-bearing)
Replace the additive score with the PP-275 rotation geometry (CITED@notes research_how_others_beat_frequency_
..._2026-07-11 + substrate_capability_map PP-275 = `exp_lap3_rotate_analogy_cpu_v1`, in-domain Hits@1=0.899):
entities = unit phasors PHI (N,k); relation = phase rotation THETA (n_rel,k); distance =
||exp(i(PHI_h+THETA_r)) - exp(i PHI_t)|| (chordal). Implemented as the smooth surrogate `d_mean =
mean_j(1-cos((PHI_h+THETA_r)_j - PHI_t,j))`, MONOTONE-IDENTICAL to PP-275's chordal-L2 ranking (unit phasors:
||exp(iq)-exp(i PHI_t)||^2 = 2k(1-cos_mean)). Keep the Anchor-1 recipe (self-adversarial CE + reciprocal +
minibatch SGD) with the LR fix (5e-3, not 0.05). The ADDITIVE_TRANSE arm uses `fit_kge_anchor1` at the SAME
recipe (lr, n_neg, batch, reciprocal) so the head-to-head isolates the FUNCTIONAL FORM, not the recipe.

## Readouts (report both)
- PRIMARY = DIRECT native score (rotation = FHRR cos-mean = PP-275 chordal ranking; additive = -||.||). This
  is the trusted readout (ladder: direct >> fpe).
- SECONDARY = FPE bounded-kernel with MEDIAN-HEURISTIC bandwidth (NOT the fixed ell=0.55 that underflowed to
  0.000). Reported for ONESHOT + ORACLE as a diagnostic: does the median-bandwidth fix recover the FPE readout?

## 0.90 oracle-fire gate DROPPED (director + scour, confirmed)
No literature precedent at this scale (best de-leaked KGE ~0.53-0.60 hits@10). The win is NOT gated on oracle
recovery. Held-out oracle recovery is CONTEXT only. The ORACLE arm's ONLY gating role is a MODEST validity
trust gate: ORACLE(direct) - RANDOM(direct) >= 0.15 (if even the transductive rotation fit cannot recover
edges it trained on, the reasoning question is not askable -> INCONCLUSIVE, not a substrate verdict).

## Arms (7; paired on the SAME held-out queries + candidate set + strata per seed)
ONESHOT_ROTATE (map arm) | ADDITIVE_TRANSE (functional-form head-to-head) | BASELINE_POP (the bar) |
SCRAMBLE_ROTATE (must-fail: relation labels shuffled) | RANDOM_CODES (null) | ORACLE_TRANSDUCTIVE (trust gate)
| DISCRETE_BIND (old failure mode).

## Bands (pre-registered)
WIN = `WINS_ROTATION_BEATS_FREQUENCY` (ALL of):
1. ONESHOT (fair low+mid) hits@10 - POP (fair) >= POP_GAP (0.03).
2. Functional-form: ONESHOT - ADDITIVE >= FORM_GAP (0.02) on the fair stratum OR ORACLE - ADDITIVE >= 0.02.
3. ONESHOT - DISCRETE >= DISCRETE_UNDER (0.03) [old failure mode underperforms].
4. SCRAMBLE - ONESHOT <= SCRAMBLE_EPS (0.03) [must-fail fires].
5. Seed-flip cv of the winning arm's fair hits@10 across seeds {7,17,23} < 0.15 (director watch-item; computed
   downstream across the 3 seed metrics files).
6. |cross_channel_geom_vs_poprank_r| < R_BACKDOOR (0.15, stricter watch-item).
7. ORACLE(direct) - RANDOM(direct) >= 0.15 [trust gate; NOT 0.9].
8. NOT broken (no must-fail control beats POP+0.02 on the fair arena).
9. SYN_COMPOSITIONAL positive control fires (rotation beats POP + additive); SYN_FREQ no-manufacture.
10. Mine params match a46eadfa: MAX_RULES_PER_HEAD=50, HUB_CAP=60000, min_support=10, min_conf=0.10.

HARD-FAIL (clean negative or broken):
- `FAILS_ROTATION_TIES_OR_LOSES`: ONESHOT (fair) - POP (fair) <= TIE_EPS (0.02) WITH ORACLE firing (fit/readout
  is not the excuse) -> the functional-form fix did not realize the L2 opportunity; closes Course C on solid,
  non-confounded ground (the single most valuable clean-negative outcome).
- `BROKEN_TEST_CONTROL_BEATS_POP`: SCRAMBLE or RANDOM beats POP by >0.02 on the fair arena -> discriminator not
  firing; do not trust any margin.
- Seed-flip cv >= 0.15 -> unstable; add seeds before any headline.
- Backdoor fires (|r| >= 0.15).

INCONCLUSIVE (validity): `INCONCLUSIVE_ORACLE_UNDERFIT` if ORACLE(direct) - RANDOM(direct) < 0.15 -> even the
rotation fit cannot recover transductive edges at this capacity; escalate (epochs/k/dim), and note the
functional-form fix did not resolve the fit wall (strong escalation signal).

MIDDLE_BAND otherwise.

Info-ceiling: ORACLE (transductive) = the fit/readout ceiling; report realized_vs_ceiling_ratio
(ONESHOT/ORACLE). CSKG opportunity ceiling: a46eadfa l2_only_all=0.276, l2_only_high=0.226, pop_high=0.412
(CITED@notes VET a46eadfa).

## BANKED FOLLOW-UP (pre-cleared next step; NOT implemented here)
If the rotation fix under-delivers specifically on the IS_A (1-to-N / hierarchical) stratum, the pre-cleared
next lever is a modulus/phase-split (RotatE-modulus style: learnable entity modulus so hierarchy targets
spread radially instead of colliding on the unit circle). Deferred by design (scour banked follow-up).

## Compute architecture
class (c) MIXED: symbolic L2/L1I/L1F + POP = sequential-CPU graph traversal (no matmul; same imported
apparatus). Rotation/additive fits = minibatch SGD (batched-GPU). Readouts = batched matmul, QUERY-CHUNKED so
the (nq,N) map is never whole (OOM fix; family OOM'd 3x). FPE-median readout (S_all N x dim complex) is the
memory driver -> exercised at FULL footprint by the GPU memory smoke first. Storage SHARDED (per-entity phase
code; per-TYPE rotations; never a global bundle). device=auto (cuda on GPU host; remote_cpu forces cpu). FULL:
overnight_queue (GPU). Per-seed PROCESS isolation: 3 separate seed wrapper cells.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = len(seeds) per process; core HARD_FAIL_CARDINALITY_BREACH if <).
- arms_differ_verified: true (>=5 distinct held-out score sigs per seed; enforced in core, asserted at self-test).
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics/write_partial + os.replace).
- except SystemExit: raise before except Exception (no BaseException / no bare except) -- grep-clean.
- crlb_n/a: filtered hits@10 chance ~ 10/n_candidates THEORETICAL; POP is the real (non-chance) bar; the WIN
  bar (geom - POP >= 0.03 on fair stratum) is on the achievable side <= the a46eadfa headroom ceiling = FAIR.
- baseline_in_band: POP is the measured confound-baseline (VET pop_high=0.412); RANDOM/DISCRETE = anti-triviality
  nulls; ORACLE = trust gate. discriminator_reachability: true (WIN bar <= a46eadfa headroom; ORACLE firing is
  the fit-adequacy proof under the direct readout, achievable given additive already reached 0.424 direct).
- calibration_check: default_ok_for_this_regime (k-core / MIN_SUPPORT / MIN_CONF / degree tertiles / mine params
  MATCH the a46eadfa VET; FPE bandwidth is median-heuristic from fitted coords, not tuned-for-PASS).
- discriminator survives scale: the geom-beats-POP discriminator IS the FULL question; the scale-invariant
  discriminator-fires proof is the grid positive control (rotation oracle fires) + SYN_COMPOSITIONAL (rotation
  beats POP + additive) run through the IDENTICAL code path in the self-test.
- baseline_in_band + AG: SYN_FREQ_GUESSABLE no-manufacture guards the saturated-frequency regime.
- sweep_alignment_verdict: ALIGNED (arm x seed x stratum; no nominal-vs-effective mismatch).
- discriminating_fraction: n/a (not a parameter sweep; 7-arm discriminator design).
- positive_control_arms: grid ORACLE reproduces transductive recovery; SYN_COMPOSITIONAL reproduces
  rotation-beats-POP AT THIS CELL'S code path before any CSKG claim. regime_extension_audit: synthetic-grid ->
  real discrete CSKG is SHAPE_DRIFT (coords FIT from graph structure) -- guarded by the coord-precision/degree
  and cross-channel backdoor checks.
- functional_requirements: (a) place gold near query under composition -> rotation fit; (b) rank vs frequency
  -> direct readout + POP baseline; (c) prove not lookup -> L2-genuine extraction (excludes L1I/L1F/known);
  (d) prove not popularity shortcut -> degree strata + backdoor r; (e) prove not manufactured -> SYN_FREQ.
- 4 validity-preflight checks DECLARED (experiments._validity_preflight, run_mode=self_test): positive_control
  (SYN_COMP rotate beats POP+additive), metric_moves (RANDOM<<POP<ONESHOT), negative_control_margin (SCRAMBLE +
  RANDOM below map by margin), full_gates_exercised (aggregate_and_verdict fires every gate at self-test scale).
- cell_chunked: true (single-seed-per-cell FULL wrappers). start_marker_written: true. crash_diagnostic_present:
  true (Exception -> CELL_CRASHED + traceback via wrapper_run). heartbeat_present: true (_heartbeat.jsonl).
  defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line_buffering + per-seed/arm flush). timeout_s >= 1800 -> flushing mandatory: satisfied.
- run_mode verification: FULL wrappers default run_mode=full (runner passes no argv); memsmoke defaults memsmoke.

## Dispatch plan (hand-off; exp_dev does not ship remote per USER lock 2026-07-08)
1. GPU MEMORY SMOKE first (overnight_queue): `exp_course_c_rotate_cskg_l2_memsmoke_v1` (2-seed, FULL memory
   footprint, 25 epochs). Confirms: self-test PASS + 4 validity checks + arms differ + oracle-direct fires + NO
   CUDA OOM across 2 seeds. Timeout 3600.
2. On memsmoke landing clean -> 3 FULL seeds (overnight_queue), per-seed process isolation: seed_7/17/23,
   timeout 14400 each (4 heavy SGD fits at ep250 over ~1M augmented edges + FPE-median readout at FULL N;
   scaled 1.5x from ladder anchor1 ep150=1073s).
