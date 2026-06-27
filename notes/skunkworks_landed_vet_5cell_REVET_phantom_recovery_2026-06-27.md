# skunkworks landed-VET 5-cell RE-VET (phantom-recovery)

## context
Prior batch refused as PHANTOM because metrics.json files weren't on disk at moment of audit.
Research re-verified file presence and asserted off-disk numbers; this RE-VET reads each
metrics.json directly via Read tool and atomizes per the verified-off-data discipline.

## verification basis
All 5 metrics.json files read end-to-end at 2026-06-27. Per-arm per-seed numbers cross-checked
against Research's paste — no discrepancies. cv computations re-verified from `per_arm_summary`
blocks (NOT from verdict_msg). META_RULE_H cardinality_ok verified per cell.

## per-cell tier rulings

### CELL 1 — pfc_controller_softmax_margin_abstain_v2 (depth-sweep [3,5,8,12])
Path: data/exp_pfc_controller_softmax_margin_abstain_v2/metrics.json
Verdict: HARD_FAIL @ depth=12 | SOFTMAX=0.156 ARGMAX=0.170 SINGLE=0.004 RANDOM=0.000 ABSTAIN=0.014
cv_softmax(d12) = 0.249 (FAILS cv<=0.10 hp)
cv_argmax(d12) = 0.214
Cardinality 100/100 OK.

Q1 (ARGMAX > SOFTMAX at d=12): partial. ARGMAX=0.170 vs SOFTMAX=0.156 = +0.014 absolute,
but both arms have cv ~0.21-0.25 which means the 0.014 gap is INSIDE noise floor. Specifically
ARGMAX per seed = [0.16, 0.11, 0.19, 0.22, 0.17] std=0.036; SOFTMAX per seed = [0.15, 0.09,
0.19, 0.20, 0.15] std=0.039. SEM_diff = sqrt(0.036^2/5 + 0.039^2/5) = 0.024 -> the 0.014
ARGMAX-over-SOFTMAX delta < 1 SEM. NOT a discriminating result on this evidence; we cannot
conclude "depth-adaptive ARGMAX is the revival" from this cell.

Q2 (cv across seeds): cv_softmax=0.249, cv_argmax=0.214 — both >2x the HP cv<=0.10 rail.
Q3 (atom tier): HONEST_NEGATIVE_DEPTH_TIER_BREAKS — at decision_depth=6 the smoke HARD_PASS
(SOFTMAX=0.383 lift=+0.378) showed mechanism works; at depth=12 SOFTMAX collapses to 0.156
with cv=0.249, ARGMAX-over-SOFTMAX gap inside noise. The TIER FINDING is real (depth>=8
appears to break PFC controller separation); ARGMAX-revival hypothesis is NOT supported by
this evidence and should be tested in a separate cell at depth=12 with higher n_seeds (n=8+)
to resolve the cv noise.

Atom 1: HONEST_NEGATIVE_DEPTH_TIER_BREAKS_FROM_DEPTH8 (delta=0).
Discipline atom (META candidate, deferred): "depth-axis cv-noise inflation" — at high
decision_depth the substrate margin compresses and seed-noise dominates; n_seeds=5 cannot
resolve sub-SEM arm differences. Track via dedicated revival cell at n_seeds=8+ if needed.

### CELL 2 — parietal_cortex_spatial_reasoning_v1
Path: data/exp_parietal_cortex_spatial_reasoning_v1/metrics.json
Verdict: MIDDLE_BAND | NO_POS_move=0.0366 FIXED_move=0.291 MOVABLE_move=0.867 REL_move=0.867
Cardinality 152000/12000 OK (over-completed).

Per-arm move_recall (movable-rebind discriminator):
  NO_POS: per seed [0.0365, 0.034, 0.041, 0.041, 0.0305] mean=0.0366 cv=0.111
  FIXED:  per seed [0.289, 0.2845, 0.2895, 0.294, 0.2965] mean=0.2907 cv=0.0144
  MOVABLE:per seed [0.8685, 0.8705, 0.867, 0.863, 0.8645] mean=0.8667 cv=0.0031
  RELATIONAL: identical to MOVABLE (arms aliased in metrics — note: per_arm
    grid_position_with_relations === grid_position_movable; the "relational" arm
    didn't actually run distinct, OR relational mechanism reuses movable arm output)

Q (MOVABLE-arm chain-grade-eligible in isolation):
  Lift-over-NO_POS (move_recall) = 0.867 - 0.0366 = +0.830 (FAR exceeds HP_lift_no_pos>=0.50)
  Lift-over-FIXED (move_recall)  = 0.867 - 0.291  = +0.576 (FAR exceeds HP_lift_fixed>=0.15)
  cv_move on MOVABLE arm        = 0.0031 (FAR under cv<=0.10 rail)
  Discriminator FIRES strongly in positive direction (META_RULE_K OK).
  fair_baseline_ok=True, suspect_1000=False (0.867 not at metric cap).
  Both FAIR rails (NO_POS + FIXED inside band [0.05, 0.95]: 0.0366 and 0.291 ✓) PASS.

RULING: MOVABLE-rebind arm IS chain-grade-eligible in isolation.
  Atom 2a: chain_grade movable-rebind (delta=+1).
  Atom 2b: honest-negative relational (REL=0.428 < HP_relational>=0.55 by 12pp; AND
    relational arm aliased to movable arm — relational mechanism not differentiated).

Net for cell 2: +1 chain-grade (movable-rebind) + 0 honest-negative (relational) = +1 CERT.

### CELL 3 — engram_dropout_inhibitory_plasticity_v2_density_matched
Path: data/exp_engram_dropout_inhibitory_plasticity_v2_density_matched/metrics.json
Verdict: MIDDLE_BAND ENGRAM_BELOW_FLOOR (engram_cor=0.147 < HP=0.40)
Cardinality 20/20 OK.

Per-arm:
  baseline_no_mask: mean_acc=0.464 mean_cor=0.223 density=1.0
  random_matched:   mean_acc=0.448 mean_cor=0.133 density=0.370
  engram_dropout:   mean_acc=0.376 mean_cor=0.145 density=0.358
  engram_dropout_dropin: mean_acc=0.376 mean_cor=0.147 density=0.371

cor_lift (engram vs random_matched) = 0.147 - 0.133 = +0.014 (HP_lift>=0.05 MISS by 36pp)
density alignment rel_diff = 0.0002 (HP<=0.10 OK; density-matched fix WORKS)

Q (HONEST_NEGATIVE for engram-dropout as importance signal at this regime):
YES. cor_lift=+0.014 is real positive direction but FAR below mechanism floor. Both arms
(engram + engram_dropin) under-perform baseline_no_mask. The dropin-rescue (delta_dropin=0.020)
recovers ~1pp cor over plain dropout but NOT meaningfully.

Density-matched-fix-works:
The density-matched random baseline IS the correct null (density_align_rel_diff=0.0002 << 0.10);
THIS METHODOLOGY validates the v1 fix — separate methodology atom warranted.

Atom 3a: HONEST_NEGATIVE engram-dropout fails as importance-signal at N=512 NCAT=25 NTRAIN=5
  alpha=0.0488 (engram_cor=0.147 vs random_matched=0.133 lift=+0.014 << HP=0.05).
Atom 3b: CHAIN_GRADE methodology: density-matched random baseline (per-pattern per-seed)
  IS the correct null for engram-dropout class; density_align_rel_diff=0.0002 confirms
  alignment. This is a load-bearing methodology atom for the wider importance-readout family.

Net for cell 3: +1 CERT (methodology chain-grade) + 0 (HF mechanism).

### CELL 4 — importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1
Path: data/exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1/metrics.json
Verdict: MIDDLE_BAND INDETERMINATE
  TRACE=0.998 (cv=0.0002 sat); PCA=0.010 (cv=8.234 lb=-0.045 NEGATIVE); Fisher_8=0.036
  Single=0.015; Rand=0.006
Cardinality 48/48 OK.

CRLB floor k=1: 0.156; CRLB floor k=8: 0.055.
ALL non-TRACE arms (PCA / Fisher / Single) sit BELOW CRLB k=8 floor (0.055) — at INSTRUMENT
NOISE FLOOR.
TRACE=0.998 at metric-cap (suspect_1000-territory but TRUE here because TRACE preserves
EVERY pattern by construction → BY_CONSTRUCTION_SATURATION).

Q (TRACE substrate-has-importance-via-existing-primitive):
  TRACE arm IS chain-grade-evidence that the existing TRACE primitive provides perfect
  importance recovery at d=16384 M=400 — BUT this is BY_CONSTRUCTION (TRACE stores all
  M patterns superposed; readout at d/M=40.96 is well above retrieval capacity ratio
  ~0.15-0.20). The TRACE result is MEASURED_MECHANISM (proven-bound at this regime;
  recovery is real but mechanism is "store everything; readout is OLS"). Not chain-grade
  for "importance signal beyond storage" because no orthogonal arm separated.

Q (INDETERMINATE needs M-scale to match TRACE regime):
  Confirmed. All readout arms (PCA/Fisher/Single) at instrument floor when TRACE saturates
  = methodology-confound (the regime is so far below TRACE storage capacity that no readout
  arm can DIFFERENTIATE). At M=16384 (matching d=16384) all arms would EITHER hit retrieval
  cliff together OR separate meaningfully. Cell at M=400 is too easy for TRACE and too hard
  for everything else.

Atom 4: MEASURED_MECHANISM TRACE-by-construction-saturation at M/d=0.024 (M=400/d=16384);
  PROVEN-BOUND that TRACE provides perfect importance recovery at FAR-BELOW-CAPACITY regime
  (d/M=40.96); OTHER readout arms at noise floor (CRLB k=8 = 0.055 separating threshold).
  INDETERMINATE for readout-arm separation; rescue cell at M=16384 to match d=16384 needed.

Net for cell 4: +0 CERT (MM not chain-grade per by-construction-saturation discipline).

### CELL 5 — btsp_binary_synapse_one_shot_v2_regime_probed
Path: data/exp_btsp_binary_synapse_one_shot_v2_regime_probed/metrics.json
Verdict: HARD_FAIL REGIME_INFEASIBLE
  Probe found 1 cfg (N=2048 NCAT=100 NTRAIN=10 noise=0.85 alpha=0.0488) with baseline=1.0
  (which is OUTSIDE band [0.40, 0.65]); NO probe cfg gave baseline IN band.
  Smoke: HARD_FAIL BASELINE_FLOOR multi-seed baseline=0.381 (just below 0.40).

Q (META_RULE_AD candidate — probe-band tolerance must absorb multi-seed SEM drift):
CONFIRMED. The probe found a 1-seed cfg at exactly baseline=1.0 (FAR above band ceiling);
multi-seed at same cfg drifted to 0.381 (just below band floor). The drift = ~0.62 in
baseline_acc across single-seed-probe vs 5-seed-full is enormous; this is the
SEM-DRIFT-NOT-IN-PROBE-TOLERANCE failure mode. Probe-band should be tightened: probe must
verify in-band ACROSS multi-seed (e.g. 3-seed probe with all 3 seeds in band) before
declaring cfg-found.

Atom 5: HONEST_NEGATIVE_REGIME_INFEASIBLE BTSP v2 at probe-tested regimes — no cfg with
  baseline_acc in [0.40, 0.65] band found across 1 probe; META_RULE_AD candidate
  documented as discipline atom (separate META atomization deferred to allow
  cell-author rescue iteration at v3 with multi-seed probe tolerance).

Net for cell 5: +0 CERT.

## net CERT delta
+2 chain_grade (cell 2 movable-rebind + cell 3 density-matched methodology) — 0 demotes = +2.
CERT N: 623 -> 625.

## ledger rows added: 7
  cell 1: 1 row (honest_negative)
  cell 2: 2 rows (chain_grade movable + honest_negative relational)
  cell 3: 2 rows (chain_grade methodology + honest_negative mechanism)
  cell 4: 1 row (measured_mechanism)
  cell 5: 1 row (honest_negative)

## 2x drill triggers
  None new. (Cell 5 META_RULE_AD candidate deferred as discipline-atomization separately;
  cell 1 depth-axis cv-noise candidate deferred pending revival cell at n_seeds=8+.)

## commit hash
Pending atomize script run + git commit.
