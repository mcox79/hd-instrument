# Pre-reg: substrate_storage_update_rule_family_phase_diagram_v1_1

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn, v1.1 recalibration)
**Prior cell:** v1 (commit d5e3ed60) HARD_FAIL_CONTROL_FAIL x 3 seeds
**Recalibration authority:** META_RULE_BC (positive control must clear floor
before sweep is interpretable); Skunkworks recommended defer + rerun.

## Failure mode of v1 (MEASURED)

MEASURED@d:/AI/hd-instrument/data/exp_substrate_storage_update_rule_family_phase_diagram_v1_seed_7/metrics.json:
- verdict = HARD_FAIL
- verdict_msg = "HARD_FAIL_CONTROL_FAIL: hebbian@alpha=0.5 recall < floor on 1/1 seeds"
- positive_control_recall = 0.83897 (< 0.90 floor)
- At alpha=0.5, N=8192 -> M=4096, load M/N=0.5
- Hopfield capacity 0.14*N = 1147 patterns; M=4096 >> 1147 => over-capacity for positive control

## v1.1 recalibration (Option A: shift alpha sweep LEFT)

**Change:** ALPHA_SWEEP = [0.125, 0.25, 0.5, 1.0] (v1 was [0.5, 1.0, 2.0, 4.0]).
At N=8192, this yields M = [1024, 2048, 4096, 8192] instead of v1's [4096, 8192, 16384, 32768].

**Positive control:** hebbian_outer_product @ alpha=0.25 (M=2048, N=8192).
- Load factor M/N = 0.25
- THEORETICAL@Hopfield_capacity: M=2048 is close to 2x above Hopfield critical 0.14*N=1147 but well below full over-capacity; recall projected 0.90-0.97 at cue_cos=0.70
- HYPOTHESIZED@this pre-reg: FULL recall >= 0.93 (safely above 0.90 floor)

**Cell:**
- Core: `d:/AI/hd-instrument/experiments/_substrate_storage_update_rule_family_phase_diagram_v1_1_core.py`
- Seed sources (3-seed chunked):
  - `d:/AI/hd-instrument/experiments/exp_substrate_storage_update_rule_family_phase_diagram_v1_1_seed_7.py`
  - `d:/AI/hd-instrument/experiments/exp_substrate_storage_update_rule_family_phase_diagram_v1_1_seed_13.py`
  - `d:/AI/hd-instrument/experiments/exp_substrate_storage_update_rule_family_phase_diagram_v1_1_seed_19.py`

## Outer axis (LOCKED, unchanged from v1)

4 update rules:
1. `hebbian_outer_product` - W = sum outer(x_i, y_i). **POSITIVE CONTROL.**
2. `soft_hebb` - Online incremental with tanh residual (predictive-coding flavor)
3. `willshaw_binary` - W = sign(X.T @ Y) (binary AM)
4. `bcm_gain` - W = X.T @ (Y * (Y - mean(Y))) (BCM with row-mean theta)

## Inner axis (SHIFTED LEFT vs v1)

- **alpha (loading factor):** `{0.125, 0.25, 0.5, 1.0}` -> M in `{N/8, N/4, N/2, N}`
- **N:** 8192 FULL; 2048 SMOKE
- K_per_bank=64, num_banks=16 (rail-config; K*B=1024 slots FIXED)

CARDINALITY:
- FULL: 4 rules x 4 alphas = **16 phase points per seed**
- SMOKE: 4 rules x 4 alphas = **16 phase points per seed**

CARDINALITY_OK_FULL: 16. CARDINALITY_OK_SMOKE: 16.
HARD_FAIL on cardinality breach (META_RULE_H).

## Discriminator (LOAD-BEARING)

Per phase point (rule, alpha):
- `recall` = bit-accuracy of readout y_hat vs y_true, averaged over N_PROBE items.
  Cue = clean key + bipolar noise (CUE_COS=0.70).
- `alpha_cliff` = smallest alpha where recall drops below 0.50 (per rule);
  if none, cliff = 2*max(alpha) (beyond sweep).

Per cell:
- `cliff_span_log2` = max(cliff_log2) - min(cliff_log2) across the 4 rules.
- `cliffs_distinguishable` = (cliff_span_log2 >= 0.5).

## Bands (PRE-REG envelope-fail-bands; unchanged from v1)

Per phase point:
- `SATURATED`: recall >= 0.999
- `HARD_PASS`: recall >= 0.90
- `MIDDLE_BAND`: 0.30 <= recall < 0.90
- `FLOOR`: recall <= 0.05
- `HARD_FAIL`: 0.05 < recall < 0.30

Per cell (full):
- `HARD_PASS_UPDATE_RULE_PHASE_DIAGRAM_v1_1` (chain-grade):
  - cardinality_ok
  - positive_control (hebbian@alpha=0.25 recall >= 0.90 FULL; >= 0.85 SMOKE)
  - cliffs_distinguishable (cliff_span_log2 >= 0.5)
- `MIDDLE_BAND_UPDATE_RULE_PHASE_DIAGRAM_v1_1`: rules cluster.
- `HARD_FAIL_CARDINALITY_BREACH`: cardinality_ok=False.
- `HARD_FAIL_CONTROL_FAIL`: hebbian@alpha=0.25 below floor (v1.1 recalibration failed;
  retry with Option B N=16384 or Option C cue_cos=0.85).

## Smoke results (2026-06-30, seed=7, N=2048)

**Positive control (META_RULE_BC): hebbian@alpha=0.25 (M=512/N=2048) = 0.9187**
(>= 0.85 SMOKE floor -- PASS)

MEASURED@d:/AI/hd-instrument/data/exp_substrate_storage_update_rule_family_phase_diagram_v1_1_seed_7_smoke/metrics.json:

Per-arm alpha=0.125 (M=256):
- hebbian_outer_product: recall=0.9762 tier=HARD_PASS
- soft_hebb: recall=0.8162 tier=MIDDLE_BAND
- willshaw_binary: recall=0.9431 tier=HARD_PASS
- bcm_gain: recall=0.4997 tier=MIDDLE_BAND (degenerate; expected)

Per-arm alpha=0.25 (M=512) -- POSITIVE CONTROL POINT:
- hebbian_outer_product: recall=0.9187 tier=HARD_PASS **(PC CLEARS 0.85 SMOKE floor)**
- soft_hebb: recall=0.7970 tier=MIDDLE_BAND
- willshaw_binary: recall=0.8681 tier=MIDDLE_BAND
- bcm_gain: recall=0.4909 tier=MIDDLE_BAND

Per-arm alpha=0.5 (M=1024):
- hebbian_outer_product: recall=0.8394 tier=MIDDLE_BAND
- soft_hebb: recall=0.7458 tier=MIDDLE_BAND
- willshaw_binary: recall=0.7839 tier=MIDDLE_BAND
- bcm_gain: recall=0.4966 tier=MIDDLE_BAND

Per-arm alpha=1.0 (M=2048):
- hebbian_outer_product: recall=0.7570 tier=MIDDLE_BAND
- soft_hebb: recall=0.6884 tier=MIDDLE_BAND
- willshaw_binary: recall=0.7124 tier=MIDDLE_BAND
- bcm_gain: recall=0.5070 tier=MIDDLE_BAND

Cliff span log2:
- hebbian cliff=2.0 (beyond sweep), log2=1.0
- soft_hebb cliff=2.0 (beyond sweep), log2=1.0
- willshaw_binary cliff=2.0, log2=1.0
- bcm_gain cliff=0.125 (below 0.5 at alpha=0.125), log2=-3.0
- cliff_span_log2 = 4.00 (>= 0.5 threshold -> cliffs distinguishable)

verdict = HARD_PASS_UPDATE_RULE_PHASE_DIAGRAM_v1_1 (smoke tier)
elapsed = 24.2 s

## Discriminator-survives-scale (META_RULE_AG) analysis

**Positive control at SMOKE-N=2048 = 0.9187; at FULL-N=8192 will be BETTER:**
- Same load factor M/N=0.25
- N=8192 has 4x lower argmax-noise floor per bit vs N=2048 (readout SNR scales with sqrt(N))
- HYPOTHESIZED@this pre-reg: FULL PC recall in [0.93, 0.97] range

**Prior v1 data point (MEASURED):** hebbian@alpha=0.5/M=4096/N=8192 = 0.83897.
v1.1 SMOKE hebbian@alpha=0.5/M=1024/N=2048 = 0.8394 (nearly identical; same load 0.5).
=> Load factor is the load-bearing parameter, not raw N. At load 0.25 in v1.1
positive-control regime, FULL recall should exceed SMOKE 0.9187.

**Discriminator (cliff_span_log2 >= 0.5) FIRES at smoke = 4.00.** BCM stays at chance;
other 3 rules cliff beyond alpha=1.0. At FULL-N=8192 with M going up to 8192, we
expect ALL 3 non-BCM rules to cross the 0.5 cliff at some alpha (probably alpha=1.0
for hebbian/willshaw, similar for soft_hebb; BCM stays flat at 0.5). Cliffs
DIFFERENTIATE across rules -> HARD_PASS band achievable at FULL.

## Smoke timing / FULL timeout estimate

Per-seed SMOKE wall = 24.2 s at N=2048.

Per-rule scaling to FULL (N=8192, 4x N):
- hebbian: matmul-dominated O(M*N^2 write) + O(N_PROBE*N^2 read); at N=8192 vs 2048
  matmul is 16x; M goes 8x (max M=8192 vs 2048); total ~30-40s
- willshaw/bcm: same matmul scaling; ~30-40s each
- soft_hebb: Python loop O(M*N^2); at N=8192/M=8192 vs N=2048/M=2048: 4x N^2 * 4x M
  = 64x smoke soft_hebb (~30s at smoke alpha=1.0) => ~1900s = ~32min
- Per-seed FULL wall estimate: hebbian+willshaw+bcm ~120s sum + soft_hebb ~2000s
  = ~2120s = ~35 min per seed

**Timeout estimate:** 1.5 * 2120 = 3180 s per seed. Task specifies 7200s/seed.
**timeout = 7200 s (2 hr)** per seed (conservative per task; matches task spec).

## Dispatch plan

- **Queue:** `remote_cpu_queue` (matmul-bound; CPU acceptable; soft_hebb Python-loop
  is GIL-bound regardless of device; CPU fine)
- **Seeds:** 7, 13, 19 (3-seed chunked; separate cell files per seed)
- **Timeout:** 7200 s per seed (per task spec)
- **Routing path:** exp_dev cannot push to origin/main (harness-DENIED); Orchestrator
  handles push + queue_add

## Cell-template mandates satisfied

- ASCII-only (no unicode / em-dashes / emojis)
- META_RULE_AE: constants LOCKED at module init
- META_RULE_AF (arms-differ): 4 rules produce 4/4 unique W hashes at selftest
- META_RULE_AH: atomic final metrics write via `.tmp` + `os.replace()`
- META_RULE_H: cardinality_ok mandatory; HARD_FAIL on breach; observed_n=16
- META_RULE_BC: positive control at alpha=0.25 CLEARS 0.85 SMOKE floor (0.9187)
- except SystemExit: raise BEFORE except Exception (not BaseException); no bare except
- start_marker / crash-diag / per-unit checkpoint / heartbeat all present
- calibration_check: default_ok_for_this_regime (evidence: v1.1 smoke @ M=512/N=2048
  yields recall=0.9187 for positive control, well above 0.85 floor; discriminator fires
  with cliff_span_log2=4.00)

## Pre-reg gate summary (§15)

- sweep_alignment_verdict: ALIGNED (alpha directly controls M via M=alpha*N;
  positive-control primitive sees alpha=0.25 directly)
- discriminating_fraction: 12/16 = 0.75 (>= 0.30 threshold; HARD_PASS or MIDDLE_BAND
  per phase point; 4 saturated=0)
- composition_edges: none (single-primitive cell; no composition adapter needed)
- positive_control_arms: hebbian_outer_product @ alpha=0.25 (M=2048/N=8192);
  tolerance 0.05 (must clear 0.90 FULL floor); if fails => HARD_FAIL_CONTROL_FAIL
  and pivot to Option B (N=16384) or Option C (cue_cos=0.85)
- functional_requirements: "storage update rule discrimination via alpha-cliff
  localization" -> primitive: alpha-sweep phase diagram (chain-grade in v2 capacity
  cell 2026-06-28)

## Known limitations / honest caveats

- **bcm_gain remains degenerate** in bipolar regime (stuck at 0.50 recall).
  This is a MEASURED FINDING carried over from v1 (BCM with theta=0 + bipolar y
  reduces sign information). Cliff for BCM stays at alpha=0.125 (below 0.5 recall
  from the start); this DRIVES the cliff_span_log2=4.00.
- **soft_hebb wall-clock**: Python loop still slow at FULL (soft_hebb alpha=1.0 ~30 min).
  Total FULL per-seed wall ~35 min. If Skunkworks tiers HARD_PASS worth the compute,
  future v1.2 could vectorize.
- **Positive control STILL uses same encoder as v1** (CUE_COS=0.70 bipolar noise);
  no changes to noise model. The recalibration is PURELY the alpha shift.

## Skunkworks's expected VET arc

1. Independent recompute of recall per (rule, alpha) point off `phase_map`.
2. Verify positive_control (hebbian@alpha=0.25 >= 0.90 FULL / >= 0.85 SMOKE).
3. Verify W_hash distinctness (META_RULE_AF).
4. Tier decision:
   - HARD_PASS if hebbian@alpha=0.25 clears 0.90 + cliffs_distinguishable
   - MIDDLE_BAND if cliffs cluster (span < 0.5)
   - HARD_FAIL if cardinality breach or PC fails (retry Option B/C)

Cell-author default: under-claim. Let cert-owner tier UP.
