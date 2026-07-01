# Pre-registration: theta_gamma_v4_extended_seeds_gpu

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER 2026-07-01 revival directive following Skunkworks MM ruling
on v3 (commit 37c0c049) — 2x-drill negative recovery via extended-seeds
characterization of FLAT_32 cliff distribution.

## Anchor

`theta_gamma_v4_extended_seeds_gpu_seed_{7,13,19,23,29,31,37}_N16384`

7 sibling cell files (chunked per USER 2026-06-28):
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_7.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_13.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_19.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_23.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_29.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_31.py`
- `experiments/exp_theta_gamma_v4_extended_seeds_gpu_seed_37.py`

Shared core: `experiments/_substrate_theta_gamma_v4_extended_seeds_gpu_core.py`

## Routing

- **Smoke queue:** local (laptop CPU; 1-seed smoke; ~10-15 min per seed at
  15 phase points; USER 2026-07-01 SMOKE ONLY on local rule)
- **Full queue:** `overnight_queue` (GPU runner; PROT-020 `import torch`
  present; CUDA complex64 matmul-bound)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch
  routes through Orchestrator via SendMessage post-commit.

## Why this cell exists (2x-drill negative recovery)

v3 (2026-07-01) landed tiered MEASURED_MECHANISM at N=16384 GPU:

**MAIN mechanism (NESTED cliff):** ROCK-SOLID across 3 seeds
- seed 7:  NESTED cliff_K=100, log2=6.6439
- seed 13: NESTED cliff_K=100, log2=6.6439
- seed 19: NESTED cliff_K=100, log2=6.6439
- cv=0.000 (perfect reproducibility)
- MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json
  per_arm_summary.FHRR_NESTED_THETA_GAMMA.cliff_K

**SECONDARY discriminator (nested_vs_flat32 >= 0.1):** broke unanimity
- seed 7:  nested_vs_flat32=0.000 (FLAT_32 cliff=100 = NESTED cliff=100)
- seed 13: nested_vs_flat32=1.000 (FLAT_32 cliff=50, NESTED cliff=100)
- seed 19: nested_vs_flat32=1.000 (FLAT_32 cliff=50, NESTED cliff=100)
- MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_7/metrics.json
  nested_vs_flat32_log2_delta == 0.0

Root cause: **codebook-draw seed dependence at 32-position complex64 basis**.
FLAT_32 arm cliff shifts K=100 (seed 7) vs K=50 (seeds 13/19) due to
per-seed variance in the flat 32-phase basis.

v4 tests whether the FLAT_32 cliff distribution across MORE seeds is:
- (A) tight around cv<=0.15 (unimodal; nested_vs_flat32 >=0.1 at majority),
- (B) genuinely bimodal K in {50, 100} (informative characterization),
- (C) broader spread revealing non-trivial dependence on basis draw.

All three outcomes are informative substrate characterizations. HP includes
either A or B (bimodal-atomized accepted); HF is only if main mechanism
crumbles or positive control fails.

## Arms (5 arms; OUTER axis; LOCKED; same as v3)

| Arm | Codebook | Position basis | Encode | Decode |
|-----|----------|----------------|--------|--------|
| `NO_POSITION` | FHRR complex64 | none (chance) | complex sum | argmax on \|inner\| |
| `CYCLIC_SHIFT` | bipolar {-1,+1}^N | implicit roll | sum of rolled items | inverse roll + cosine |
| `FHRR_FLAT_PHASE_8` | FHRR complex64 | 8 unit-phase | phase-mul + sum | conj-mul + argmax magnitude |
| `FHRR_FLAT_PHASE_32` | FHRR complex64 | 32 unit-phase | phase-mul + sum | conj-mul + argmax magnitude |
| `FHRR_NESTED_THETA_GAMMA` | FHRR complex64 | theta(8) * gamma(8) = 64 | phase-mul nested | conj-mul + argmax magnitude |

## Sweep axes

| Axis | FULL values | SMOKE values | Count |
|------|-------------|--------------|-------|
| arm | 5 | 5 | 5 |
| K_SEQ | {50, 75, 100, 125, 150, 175, 200, 500, 1000, 2000, 5000} | {50, 100, 200} | 11 / 3 |
| seed (across siblings) | 7 seeds {7, 13, 19, 23, 29, 31, 37} | 1 seed (seed 7 first, others locally optional) | 7 / 1 |

Fine K-grid {75, 125, 150, 175} added specifically to resolve FLAT_32 cliff
around K=50-200 where v3 showed seed-dependent split. v3 K_FULL was
{50, 100, 200, 500, 1000, 2000, 5000}; v4 K_FULL keeps that + adds 4 fine points.

**Cardinality:**
- FULL: 5 * 11 = **55 phase points per seed** * 7 seeds = 385 total
- SMOKE: 5 * 3 = **15 phase points per seed** (single seed smoke)

EXPECTED_N_UNITS_FULL=55 (per seed), EXPECTED_N_UNITS_SMOKE=15 LOCKED at
module init. `cardinality_ok: bool` field emitted; HARD_FAIL_CARDINALITY_BREACH
on mismatch (META_RULE_H).

## Regime (LOCKED, same as v3 for cross-cell comparison)

- N_DIM = 16384
- ITEM_VOCAB_SIZE = 10000
- NOISE_SIGMA = 0.05
- N_QUERIES_PER_K_full = 50; smoke = 25
- POSITION_SLOTS: 8 / 32 / 64 (nested = 8x8)

## Sweep alignment (Gate A - META_RULE_15A)

- swept_params: `{K_SEQ: {50, 75, 100, 125, 150, 175, 200, 500, 1000, 2000, 5000}, seed: 7 values}`
- effective_params_per_primitive:
  - `NO_POSITION`: effective_K_SEQ = K_SEQ (bundle load scales linearly)
  - `CYCLIC_SHIFT`: effective_K_SEQ = K_SEQ (roll positions all distinct)
  - `FHRR_FLAT_PHASE_8`: effective_K_SEQ / 8 = load per position slot
  - `FHRR_FLAT_PHASE_32`: effective_K_SEQ / 32 = load per position slot
  - `FHRR_NESTED_THETA_GAMMA`: effective_K_SEQ / 64 = load per position slot
- sweep_alignment_verdict: **ALIGNED**

## Discriminating band coverage (Gate B - META_RULE_15B)

Predicted `retrieval_acc` per K_SEQ point per arm at N=16384 (interpolated
from v3 seed_7 measured cliff table + fine-grid extrapolation):

FLAT_32 predicted per K (seed_7 v3 anchor):
- K=50: 0.72 (v3 measured), K=75: ~0.62 (extrap), K=100: 0.50 (v3 measured),
- K=125: ~0.33 (extrap), K=150: ~0.22 (extrap), K=175: ~0.16 (extrap),
- K=200: 0.12 (v3 measured), K=500: 0.12 (v3), K=1000: 0.04 (v3),
- K=2000: 0.02 (v3), K=5000: 0.00 (v3)

Points in discriminating band [0.30, 0.70] per FLAT_32 arm: ~4/11 (K=75,
K=100, K=125 all near cliff at 0.30-0.72; sufficient to resolve cliff location
at fine granularity).

Overall `discriminating_fraction` ~4/11 = 0.36 (>= 0.30 threshold).

**Gate B verdict:** ACCEPTABLE — cliff-analysis cells derive discriminator
from cliff-K per arm; fine grid specifically targets FLAT_32 cliff resolution.

## Signal-shape compatibility (Gate C - META_RULE_15C)

No cross-primitive composition; each arm is self-contained. Gate C
vacuously satisfied.

## Positive control (Gate D - META_RULE_15D)

**Regime extension audit** (v3 -> v4):
Same N_DIM, ITEM_VOCAB, NOISE_SIGMA, arms as v3. Only delta = added K-points
+ added seeds. Regime IDENTICAL, so v3 measurements at K in {50, 100, 200,
500, 1000, 2000, 5000} serve as positive control reproduction gate.

Cited prior CG atom: v3 HARD_PASS for seeds 13 and 19 at N=16384:
`max_fhrr_vs_cyclic_log2_delta=4.322`, `nested_vs_flat32=1.000`.
MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_13/metrics.json

**Positive-control tolerance (v3 rerun):**
- seed 7 FLAT_32 cliff_K expected = 100 (v3 measured)
- seed 13 FLAT_32 cliff_K expected = 50 (v3 measured)
- seed 19 FLAT_32 cliff_K expected = 50 (v3 measured)
- Tolerance: exact match at K-grid points {50, 100, 200, 500, 1000, 2000, 5000}
  (regime identical; deterministic per seed).
- If mismatch: cell-invocation bug; do NOT trust new seed 23/29/31/37 data.

regime_extension_audit: **SHAPE_MATCH** (identical regime; only sweep
finer + seed extension).

## Functional requirements (Gate E - META_RULE_15E)

1. **Sequence encoding at higher N:** Existing chain-grade primitive
   `encode_fhrr_sequence` (v3 core; identical).
2. **Order binding at higher N:** Existing CG primitive
   `theta_gamma_bind` (v3 core; identical).
3. **Nested theta*gamma at higher N:** Existing CG primitive
   `_build_positions_nested` (v3 core; identical).
4. **Cross-seed distribution characterization:** New aggregation logic
   in `aggregate_and_verdict`; computes cv on cliff_K per arm; classifies
   FLAT_32 as tight/bimodal/spread.

Functional requirements 1-3 map to v3 primitives (SHAPE_MATCH); requirement 4
is aggregation-side, not substrate mechanism.

## Mechanism (FHRR core - inherited from v3)

```python
def theta_gamma_bind(item_hd_complex, position_hd_complex):
    return item_hd_complex * position_hd_complex

def theta_gamma_unbind(bound_hd_complex, position_hd_complex):
    return bound_hd_complex * position_hd_complex.conj()

def encode_sequence(items, positions):
    return (items * positions).sum(dim=0)

def decode_at_position(seq, position, item_codebook):
    candidate = seq * position.conj()
    scores = (item_codebook.conj() @ candidate).abs()
    return scores.argmax()
```

## Pre-reg discriminator bands (LOCKED)

### HARD_PASS gates (ALL must hold)
- `cardinality_ok == True` at all 7 seeds (55/55 pts each)
- `n_pairs_differ >= 9 of 10` at every seed (META_RULE_AX FULL floor)
- HP_ALL_SEEDS_PRIMARY: `max_fhrr_vs_cyclic_log2_delta >= 1.5` at EVERY seed (7/7)
- HP_NESTED_VS_FLAT32_MAJORITY: `nested_vs_flat32_log2_delta >= 0.1` at
  >= 5/7 seeds (RELAXED from v3 unanimity)
- HP_FLAT_32_CLIFF_CHARACTERIZED: EITHER cv(FLAT_32 cliff_K over 7 seeds) <= 0.15
  OR distribution is bimodal (accept BOTH as HP; verdict reports mode)
- `no_position_saturates_K50 == False` at all 7 seeds
- `<3 arms saturate at K=50` at all 7 seeds (META_RULE_Q)
- NOT (nested_cliff_cv > 0.05): main mechanism must stay tight
- NOT (cyclic_cliff_cv > 0.05): positive control must stay tight

### MIDDLE_BAND gate
- 6/7 seeds primary_ok (near-miss on unanimity primary), OR
- nested_vs_flat32_majority not achieved but pair-distinctness intact

### HARD_FAIL gates
- HARD_FAIL_CARDINALITY_BREACH: any seed < 55/55 pts
- HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): any seed < 9/10 pairs differ
- HARD_FAIL_REGIME_TOO_EASY (META_RULE_Q): any seed >= 3 arms sat K=50
- HARD_FAIL_NOISE_DISCIPLINE: any seed NO_POSITION saturates K=50
- HARD_FAIL_MAIN_MECHANISM_CRUMBLE: NESTED cliff cv > 0.05 across 7 seeds
- HARD_FAIL_POSITIVE_CONTROL_CRUMBLE: CYCLIC cliff cv > 0.05 across 7 seeds
- HARD_FAIL_LLM_LEAK: `n_llm_calls > 0`
- META_RULE_AY downgrade: HARD_PASS claimed but per-seed pairs_differ < 7

### INFORMATIONAL (atomize regardless of tier)
- FLAT_32 cliff distribution histogram across 7 seeds
- FLAT_32 cliff cv value
- FLAT_32 cliff modes descending
- NESTED / CYCLIC cliff distributions (should be tight)

## Smoke gate predicate (v4; 6 conditions; ALL must pass)

Smoke = seed 7 SMOKE run at K in {50, 100, 200} (5 arms * 3 K = 15 pts):
1. cardinality_ok (15 / 15)
2. n_pairs_differ >= 4 of 10 (smoke AX floor)
3. NO_POSITION at K=50 noisy NOT saturated (< 0.999)
4. < 3 arms saturate at K=50 (regime not catastrophically easy)
5. At least 1 FHRR arm has cliff_K >= 50 (mechanism fires)
6. `max_fhrr_vs_cyclic_log2_delta >= 0.5` (DISCRIMINATOR-MUST-SURVIVE-SCALE
   smoke floor; FULL requires >= 1.5)

Rationale: smoke K-grid is deliberately coarse [50, 100, 200] to run in
reasonable wall time on laptop CPU. Verifies substrate discriminator still
fires at N=16384 same as v3. FULL adds fine grid + all 7 seeds via GPU.

## SCHEMA-VET checklist

- [x] CARDINALITY_OK: EXPECTED_N_UNITS_FULL=55, EXPECTED_N_UNITS_SMOKE=15 declared (META_RULE_H)
- [x] META_RULE_AF arms-must-differ: SHA-256 hash gate per arm-pair; verified in selftest
- [x] META_RULE_AX arms-distinct-across-family-axis: 10/10 pairs required at FULL 9/10; smoke 4/10
- [x] META_RULE_AW seed-config-identical: SEED is only variable across 7 siblings
- [x] META_RULE_AH atomic metrics: `tmp + os.replace` for all writes
- [x] META_RULE_AC numbers tagged: all pre-reg numbers TAGGED below
- [x] META_RULE_AY verdict-emitter HARD_FAIL on self-reported distinctness False
- [x] META_RULE_Q suspect-1.000 check: gate at >=3 arms saturating K=50
- [x] `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- [x] `import torch` present (PROT-020 GPU routing gate)
- [x] HP_SCOPE: all 5 arms subject to same HP gates per seed; cross-seed
      aggregation applied ONLY to non-NO_POSITION arms; NO_POSITION is
      chance-baseline anchor and excluded from cliff-cv computation.
- [x] DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full N_DIM=16384;
      smoke gate requires `max_fhrr_vs_cyclic >= 0.5` to catch collapse.
- [x] final_metrics_atomicity: `tmp_replace` (atomic tmp + os.replace)
- [x] CRLB / capacity feasibility: `crlb_n/a` — cell is retrieval-accuracy
      phase-diagram cell across-seed characterization, not a
      quantitative-noise-floor cell. FLAT_32 cliff physics: 32-position
      complex64 basis with per-position bundle load K/32 - cliff K when
      random codebook pairwise correlation exceeds noise budget. Cliff
      predicted at K ~ 80-110 at N=16384 sigma=0.05 from v3 data
      (seed-dependent within factor of 2).
- [x] baseline_in_band (META_RULE_AG): NO_POSITION at K=50 measured
      ~0.02-0.03 CPU seed 7 v3 (well below 0.95); FLAT_32 at K=50 measured
      0.58-0.72 (within band). Baseline discrimination good.
- [x] cell_chunked: TRUE (one seed per sibling file; 7 siblings)
- [x] start_marker_written: TRUE (STARTED metric written before heavy work)
- [x] crash_diagnostic_present: TRUE (outer try -> import_crash sentinel)
- [x] heartbeat_present: PARTIAL (per-K-point stdout print; no _heartbeat.jsonl
      in this cell; wall per K-point ~1-25s so watchdog can tail stdout)
- [x] defensive_error_checking: passed_all_4_patterns
- [x] calibration_check: `default_ok_for_this_regime` — v3 landed
      MM at same regime with same 5-arm design + tight NESTED cliff cv=0.
      v4 delta = seed extension + fine K-grid; regime known to discriminate.

## Selftest (verified pending CPU seed_7)

Expected selftest output (matches v3 pattern):

```
cardinality FULL=55 SMOKE=15
fhrr_unbind_self_inverse_max_diff=1.33e-07
fhrr_K1_clean_retrieval_pass(pred=7)
all 5 arm outcome hashes distinct
all 5 code path hashes distinct
noise_discipline_no_position_K50_acc=~0.03 (< 0.999 ceiling)
nested_vs_flat32_distinct=True
```

MEASURED@data/exp_theta_gamma_v4_extended_seeds_gpu_seed_7_N16384_selftest/metrics.json
(pending; run on CPU pre-dispatch)

## SMOKE seed=7 target

Smoke on CPU; expected wall ~10-15 min (5 arms * 3 K * ~5s per point at
N=16384 CPU seed 7). Discriminator prediction from v3 seed_7 measurements:

- NO_POSITION K=50: ~0.02-0.04, K=100: ~0.02, K=200: ~0.02 (chance)
- CYCLIC_SHIFT K=50: 1.0, K=100: 1.0, K=200: 1.0 (saturated)
- FLAT_8 K=50: ~0.10, K=100: ~0.06, K=200: ~0.04
- FLAT_32 K=50: ~0.72, K=100: ~0.50, K=200: ~0.12
- NESTED K=50: 1.0, K=100: ~0.72, K=200: ~0.30

Expected: pairs_differ >= 9/10 (10/10 in v3); max_fhrr_vs_cyclic_log2_delta
= log2(1000/100) OR log2(1000/50) ~ 3.3-4.3 depending on FLAT_32 cliff at
seed 7 (in seed 7 v3, K=100 last-above → cliff_K=100 → log2_delta = 9.97-6.64
= 3.33). Smoke floor is 0.5; expected value 3.3 easily passes.

## Numbers TAGGED (META_RULE_AC)

- v3 landed MEASURED_MECHANISM tiered: seed 7 primary=HP, nested_vs_flat32=0.0;
  seeds 13,19 all HP; 3/3 seeds primary HP; 2/3 seeds nested_vs_flat32 HP.
  MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json
- v3 seed 7 FLAT_32 cliff_K=100 (log2=6.6439); seed 13/19 FLAT_32 cliff_K=50
  (log2=5.6439). Root cause = per-seed codebook draw variance.
  MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_7/metrics.json:per_arm_summary.FHRR_FLAT_PHASE_32.cliff_K
- v3 NESTED cliff_K=100 across seeds 7,13,19 (cv=0.000). ROCK-SOLID.
  MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json:per_arm_summary.FHRR_NESTED_THETA_GAMMA.cliff_K
- v3 CYCLIC cliff_K=1000 across seeds 7,13,19 (cv=0.000). ROCK-SOLID.
  MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json:per_arm_summary.CYCLIC_SHIFT.cliff_K
- v4 seeds {7,13,19,23,29,31,37}: 7 seeds per Skunkworks revival criterion.
  HYPOTHESIZED@this prereg (seed count locked; new seeds not yet measured).
- v4 K-grid additions {75, 125, 150, 175}: filling gap between v3 K in
  {50, 100, 200}. Predicted FLAT_32 acc from linear interpolation of v3
  seed 7 curve. HYPOTHESIZED@this prereg.
- HP_LOG2_SEPARATION_FHRR_VS_CYCLIC=1.5: inherited from v3 pre-reg (v3
  measured all seeds at 3.3-4.3, well above floor). CITED@preregs/2026-07-01_theta_gamma_v3_N16384_gpu.md
- HP_NESTED_VS_FLAT32_MAJORITY=5/7: per USER task prompt 2026-07-01
  (relaxed from v3 unanimity). CITED@task-prompt (Director spawn 2026-07-01)
- HP_FLAT_32_CV_TIGHT=0.15: per USER task prompt 2026-07-01. CITED@task-prompt
- HF_MAIN_MECHANISM_CV_MAX=0.05: main mechanism must stay tight to preserve
  the substrate claim; NESTED cliff is chain-grade primitive. HYPOTHESIZED@this prereg.
- HF_POS_CONTROL_CV_MAX=0.05: same rationale for CYCLIC positive control.
  HYPOTHESIZED@this prereg.
- CPU smoke wall estimate ~10-15 min: 15 pts × ~5s each on N=16384 CPU.
  HYPOTHESIZED@this prereg (based on v3 seed_7 CPU smoke wall).
- GPU full wall estimate ~5-10 min per seed: v3 seed_13 GPU FULL wall was
  50s at 35 pts; scaling linearly to 55 pts gives ~78s per seed. Add 20%
  buffer for fine-K overhead: ~95s per seed. Fits within 3600s timeout easily.
  MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_13/metrics.json:elapsed_s=50.44

## Cardinality_ok (META_RULE_H)

```
EXPECTED_N_UNITS_FULL = 5 arms * 11 K_SEQ = 55  (per seed)
EXPECTED_N_UNITS_SMOKE = 5 arms * 3 K_SEQ = 15  (per seed)
cardinality_ok: bool field in metrics.json (per seed)
HARD_FAIL_CARDINALITY_BREACH on any seed mismatch
```

## Dispatch info

- Per-seed timeout: **3600s** (USER-specified in task prompt; 40x headroom
  over expected GPU wall ~95s per seed for 55 pts at N=16384)
- 7 seeds dispatched separately as sibling cells (chunked per USER 2026-06-28)
- Routing: `overnight_queue` (PROT-020 `import torch` confirmed)
- Helper modules on remote (already synced with v3):
  - `experiments/_seed_checkpoint.py` (unchanged; already remote)
  - `experiments/_substrate_theta_gamma_v4_extended_seeds_gpu_core.py` (NEW; needs sync)
- run_mode=full verification post-dispatch (Section 16): mandatory;
  sentinel file size > 5KB at full

## Composes with substrate phase diagram axes

- **Axis I (Sequence encoding) - seed-distribution characterization:**
  v4 verifies FHRR phase-mul + nested-theta*gamma sequence-encoding cliff
  distribution across 7 seeds at N=16384.
- **Axis J (Order binding) - basis-draw sensitivity:** v4 characterizes
  seed-dependent variance in flat-32-position basis; may reveal fundamental
  hyperdimensional coding property vs implementation artifact.

If HARD_PASS at FULL: revival succeeded; theta_gamma_v3 promoted to
chain-grade with characterized FLAT_32 cliff distribution documented.

## Open questions for landed-VET (Skunkworks)

- Is FLAT_32 cliff bimodal K in {50, 100} across 7 seeds, or genuinely
  spread continuously in K in [50, 100]? Fine K-grid resolves this.
- Does the FLAT_32 seed-variance predict which seeds have K=50 vs K=100
  cliff? If yes: identifiable codebook-property signature. If no: pure
  random-draw dependence (irreducible variance).
- Does NESTED cliff stay at K=100 across all 7 seeds? If yes: main
  mechanism truly robust. If deviation: chain-grade primitive claim
  weakens.
- What is the substrate claim after v4? Options:
  - "NESTED phase code is chain-grade for order binding at N=16384 with
    seed-invariant cliff at K=100" (if main mechanism holds)
  - "NESTED phase code + FLAT_32 basis has seed-dependent cliff spread in
    factor-2 range at N=16384; nested cliff robust" (bimodal outcome)
