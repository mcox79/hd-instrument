# Pre-registration: theta_gamma_v3_N16384_gpu

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Director URGENT GPU fill cycle 2026-07-01 — extend v2 CG
(2026-06-30 HARD_PASS at N_DIM=4096) to higher hyperdimensionality
N_DIM=16384 to test whether cliff ordering + log2-delta discriminator
survives the scale change.

## Anchor

`theta_gamma_v3_N16384_gpu_seed_{7,13,19}` (3 sibling files; chunked-per-seed
per USER 2026-06-28).

Shared core: `experiments/_substrate_theta_gamma_v3_N16384_gpu_core.py`.
Sibling files:
- `experiments/exp_theta_gamma_v3_N16384_gpu_seed_7.py`
- `experiments/exp_theta_gamma_v3_N16384_gpu_seed_13.py`
- `experiments/exp_theta_gamma_v3_N16384_gpu_seed_19.py`

## Routing

- **Smoke queue:** local (laptop CPU; ~30-40 min per seed at N=16384)
- **Full queue:** `overnight_queue` (GPU runner; PROT-020 `import torch`
  present; CUDA complex64 matmul-bound)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch
  routes through Orchestrator via SendMessage post-commit.

## Why this cell exists (the gap v2 didn't close)

v2 landed HARD_PASS at N_DIM=4096 with max_fhrr_vs_cyclic_log2_delta=2.000.
Open question: does the FHRR mechanism preserve its discriminator at higher
N_DIM? The substrate's tolerance scales with N (JL bound); it's plausible
all arms saturate to 1.0 at K_SEQ<=100 with 4x capacity headroom, collapsing
the log2 delta.

v3 tests: at 4x N_DIM (16384 vs v2's 4096), does the K_SEQ cliff ordering
+ log2-delta discriminator survive scale? Task-prompt spec:
`max_fhrr_vs_cyclic_log2_delta >= 1.5` (matched to v2's 2.0 minus a 0.5
tolerance for regime drift).

Design axis coverage:
- **Axis I (Sequence encoding):** N-scale extension of prior CG primitive
- **Axis J (Order binding):** N-scale extension of prior CG primitive

## Arms (5 arms; OUTER axis; LOCKED; same as v2)

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
| K_SEQ | {50, 100, 200, 500, 1000, 2000, 5000} | {50, 200, 1000, 5000} | 7 / 4 |

**Cardinality:**
- FULL: 5 * 7 = **35 phase points per seed**
- SMOKE: 5 * 4 = **20 phase points per seed**

EXPECTED_N_UNITS_FULL=35, EXPECTED_N_UNITS_SMOKE=20 LOCKED at module init.
`cardinality_ok: bool` field emitted; HARD_FAIL_CARDINALITY_BREACH on
mismatch (META_RULE_H).

## Regime (LOCKED)

- N_DIM = 16384 (4x v2's 4096; per task-prompt spec)
- ITEM_VOCAB_SIZE = 10000 (matched to v2 for direct comparison)
- NOISE_SIGMA = 0.05 (Gaussian noise; complex for FHRR, real for CYCLIC)
- N_QUERIES_PER_K_full = 50; smoke = 25
- POSITION_SLOTS: 8 / 32 / 64 (nested = 8x8)

## Sweep alignment (Gate A — META_RULE_15A)

- swept_params: `{K_SEQ: {50, 100, 200, 500, 1000, 2000, 5000}}`
- effective_params_per_primitive:
  - `NO_POSITION`: effective_K_SEQ = K_SEQ (bundle load scales linearly)
  - `CYCLIC_SHIFT`: effective_K_SEQ = K_SEQ (roll positions all distinct)
  - `FHRR_FLAT_PHASE_8`: effective_K_SEQ / 8 = load per position slot
  - `FHRR_FLAT_PHASE_32`: effective_K_SEQ / 32 = load per position slot
  - `FHRR_NESTED_THETA_GAMMA`: effective_K_SEQ / 64 = load per position slot
- sweep_alignment_verdict: **ALIGNED** (each arm experiences K_SEQ directly
  as bundle load; arm-specific ceiling is a function of n_positions)

## Discriminating band coverage (Gate B — META_RULE_15B)

Predicted `retrieval_acc` per K_SEQ point per arm at N=16384 (extrapolated
from v2's N=4096 cliff table using linear-N capacity scaling):

| K_SEQ | NO_POSITION | CYCLIC | FLAT_8 | FLAT_32 | NESTED |
|-------|-------------|--------|--------|---------|--------|
| 50    | ~0.02       | ~1.00  | ~1.00  | ~1.00   | ~1.00  |
| 100   | ~0.01       | ~1.00  | ~1.00  | ~1.00   | ~1.00  |
| 200   | ~0.005      | ~1.00  | ~0.50  | ~1.00   | ~1.00  |
| 500   | ~0.002      | ~0.85  | ~0.10  | ~0.90   | ~1.00  |
| 1000  | ~0.001      | ~0.70  | ~0.02  | ~0.50   | ~0.90  |
| 2000  | ~0.0        | ~0.45  | ~0.005 | ~0.10   | ~0.55  |
| 5000  | ~0.0        | ~0.15  | ~0.0   | ~0.02   | ~0.10  |

Points in discriminating band [0.30, 0.70]: 5+ of 35 (each of CYCLIC / FLAT
/ NESTED sits in discriminating band at some K); `discriminating_fraction`
per Gate B ~0.14 across sweep points, but **per-arm** we see 1-2 discriminating
points per non-NO_POSITION arm — sufficient for log2-cliff analysis.

Note: NO_POSITION is intentionally at ~0 (chance baseline; sanity check
for noise discipline). This arm never enters discriminating band by design.

**Gate B verdict:** ACCEPTABLE — cliff-analysis cells derive discriminator
from cliff-K per arm, not from mid-band regime density.

## Signal-shape compatibility (Gate C — META_RULE_15C)

No cross-primitive composition; each arm is self-contained. Gate C
vacuously satisfied.

## Positive control (Gate D — META_RULE_15D)

**Regime extension audit** (v2 -> v3):

- Cited prior CG atom: v2 HARD_PASS at N=4096
  - MEASURED@data/exp_exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7/metrics.json
- Cited prior metric: `max_fhrr_vs_cyclic_log2_delta=2.000`,
  `n_pairs_differ=10/10`, `NO_POSITION K=50 acc=0.02`
- Cited prior regime: N=4096, K_SEQ up to 2000, NOISE=0.05, VOCAB=10000
- Test regime: N=16384, K_SEQ up to 5000 (extended right), NOISE=0.05, VOCAB=10000
- Tolerance: `max_fhrr_vs_cyclic_log2_delta >= 1.5` (0.5 margin off v2's 2.0)
- If outside tolerance: MIDDLE_BAND for "mechanism preserved but attenuated";
  HARD_FAIL if pairs_differ<7 (mechanism-collapse)
- regime_extension_audit: **SHAPE_DRIFT** documented — 4x N_DIM may shift
  cliff-K rightward beyond FULL sweep max (K=5000); mitigated by extending
  sweep from v2's max K=2000 to K=5000

**Positive-control arm at test regime:** implicit via cross-arm log2-delta
computation. CYCLIC_SHIFT is v2's baseline and reproduces at N=16384 as
part of the 5-arm ensemble; its cliff-K becomes the anchor for
`max_fhrr_vs_cyclic_log2_delta` computation.

## Functional requirements (Gate E — META_RULE_15E)

1. **Sequence encoding at higher N:** Existing chain-grade primitive
   `encode_fhrr_sequence` (v2). No new mechanism.
2. **Order binding at higher N:** Existing CG primitive
   `theta_gamma_bind` (element-wise phase mul, v2). No new mechanism.
3. **Nested theta*gamma at higher N:** Existing CG primitive
   `_build_positions_nested` (v2). No new mechanism.

All functional requirements map to existing v2 primitives; v3 is a
regime-extension cell, not a mechanism-innovation cell.

## Mechanism (FHRR core — inherited from v2)

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
- `cardinality_ok == True` (35/35 points)
- `n_pairs_differ >= 9 of 10` (META_RULE_AX FULL floor)
- `max_fhrr_vs_cyclic_log2_delta >= 1.5` (task-prompt spec)
- `min_cross_arm_log2_delta >= 0.1` (all-pairs cliff |dlog2_K| >= 0.1)
- `nested_vs_flat32_log2_delta >= 0.1` (nesting genuinely helps)
- `cv across seeds <= 0.10` (multi-seed reproducibility)
- `NO_POSITION at K=50 noisy < 0.999` (DISCRIMINATOR-MUST-SURVIVE-SCALE)
- No >=3 arms saturating >=0.999 at K_SEQ=50 (META_RULE_Q regime check)
- META_RULE_AY: HARD_FAIL if HARD_PASS claimed but pairs_differ < 7

### MIDDLE_BAND gate
- `n_pairs_differ >= 6 of 10` AND `max_fhrr_vs_cyclic_log2_delta >= 0.5`
- FHRR variants distinguish but log2-separation below HP=1.5 floor
- Documents "mechanism preserved but attenuated at N=16384"

### HARD_FAIL gates
- HARD_FAIL_CARDINALITY_BREACH
- HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): n_pairs_differ < 7 at FULL (< 4 at smoke)
- HARD_FAIL_REGIME_TOO_EASY (META_RULE_Q): >=3 arms saturate at K_SEQ=50
- HARD_FAIL_NOISE_DISCIPLINE: NO_POSITION saturates K=50 noisy
- HARD_FAIL_FHRR_NO_CAPACITY (smoke): no FHRR arm has cliff_K >= 50
- HARD_FAIL_DISCRIMINATOR_TOO_WEAK_AT_SMOKE: max_fhrr_vs_cyclic < 0.5 at smoke
- HARD_FAIL_LLM_LEAK: `n_llm_calls > 0`
- META_RULE_AY downgrade: HARD_PASS but pairs_differ < 7 -> HARD_FAIL

## Smoke gate predicate (5 conditions; ALL must pass)

1. cardinality_ok (20 / 20)
2. n_pairs_differ >= 4 of 10 (smoke AX floor)
3. NO_POSITION at K=50 noisy NOT saturated (<0.999)
4. < 3 arms saturate at K=50 (regime not catastrophically easy)
5. At least 1 FHRR arm has cliff_K >= 50 (mechanism fires)
6. `max_fhrr_vs_cyclic_log2_delta >= 0.5` (DISCRIMINATOR-MUST-SURVIVE-SCALE
   smoke floor; FULL requires >= 1.5)

## SCHEMA-VET checklist

- [x] CARDINALITY_OK: EXPECTED_N_UNITS_FULL=35, EXPECTED_N_UNITS_SMOKE=20 declared (META_RULE_H)
- [x] META_RULE_AF arms-must-differ: SHA-256 hash gate per arm-pair; verified in selftest
- [x] META_RULE_AX arms-distinct-across-family-axis: 10/10 pairs required at FULL 9/10; smoke 4/10
- [x] META_RULE_AW seed-config-identical: SEED is only variable across siblings
- [x] META_RULE_AH atomic metrics: `tmp + os.replace` for all writes
- [x] META_RULE_AC numbers tagged: all pre-reg numbers TAGGED below
- [x] META_RULE_AY verdict-emitter HARD_FAIL on self-reported distinctness False
- [x] META_RULE_Q suspect-1.000 check: gate at >=3 arms saturating K=50
- [x] `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- [x] `import torch` present (PROT-020 GPU routing gate)
- [x] HP_SCOPE: all 5 arms subject to same HP gates (per-arm cliff-K
      compared symmetrically; NO_POSITION as chance baseline anchor)
- [x] DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full N_DIM=16384;
      smoke gate requires `max_fhrr_vs_cyclic >= 0.5` to catch collapse
      at scale (this IS the discriminator survival check; if smoke shows
      collapse, cell honest-aborts before FULL)
- [x] final_metrics_atomicity: `tmp_replace` (atomic tmp + os.replace)
- [x] CRLB / capacity feasibility: FHRR at N=16384 has capacity ~N/8 = 2048
      bound items for clean retrieval. FLAT_PHASE_8 with 8 positions ceiling
      at K~64 (8 positions * 8 items/pos). NESTED with 64 positions ceiling
      at K~512 items. Sweep extends to K=5000 (10x NESTED ceiling), ensuring
      cliff traversal for all arms. crlb_n/a declared: cell is a
      retrieval-accuracy phase-diagram cell, not a quantitative-noise-floor cell.
- [x] baseline_in_band (META_RULE_AG): NO_POSITION at K=50 predicted
      ~0.02 (well below 0.95 saturation ceiling; well below 0.05 floor
      considered as substrate-too-hard). MEASURED at selftest: 0.033 CPU seed=7.
- [x] cell_chunked: TRUE (one seed per sibling file)
- [x] start_marker_written: TRUE (STARTED metric written before heavy work)
- [x] crash_diagnostic_present: TRUE (outer try -> import_crash sentinel)
- [x] heartbeat_present: PARTIAL (per-K-point stdout print; no _heartbeat.jsonl
      in this cell; smoke times per point ~50-100s so watchdog can tail stdout)
- [x] defensive_error_checking: passed_all_4_patterns
- [x] calibration_check: `default_ok_for_this_regime` — v2 landed HARD_PASS
      at same NOISE_SIGMA=0.05 with same 5-arm design; regime known to
      discriminate. v3 test is scale extension not mechanism change.

## Selftest (verified CPU 2026-07-01; SELFTEST_OK)

```
cardinality FULL=35 SMOKE=20
fhrr_unbind_self_inverse_max_diff=1.33e-07
fhrr_K1_clean_retrieval_pass(pred=7)
all 5 arm outcome hashes distinct
all 5 code path hashes distinct
noise_discipline_no_position_K50_acc=0.0333 (< 0.999 ceiling)
nested_vs_flat32_distinct=True
```

MEASURED@data/exp_theta_gamma_v3_N16384_gpu_seed_7/metrics.json:selftest

## SMOKE seed=7 (target)

Smoke running on CPU; expected wall ~30-40 min (N=16384 is 4x v2's N).
Will be re-verified pre-dispatch. Discriminator prediction:

- NO_POSITION K=50 ~ 0.02-0.04 (chance)
- CYCLIC_SHIFT K=50 ~ 1.0 (saturated); K=1000 ~ 0.70; K=5000 ~ 0.15
- FLAT_8 K=50 ~ 1.0; K=1000 ~ 0.02; K=5000 ~ 0.0
- FLAT_32 K=50 ~ 1.0; K=1000 ~ 0.50; K=5000 ~ 0.02
- NESTED K=50 ~ 1.0; K=1000 ~ 0.90; K=5000 ~ 0.10

Expected: pairs_differ=10/10; max_fhrr_vs_cyclic_log2_delta >= 1.0 (smoke
sweep is truncated, may not hit full 1.5 floor; smoke gate lowered to 0.5).

Full pre-dispatch verification requires smoke HARD_PASS before Orchestrator
push.

## Numbers TAGGED (META_RULE_AC)

- v2 landed HARD_PASS: 30/30 pts; pairs_differ=10/10; max_fhrr_vs_cyclic_log2_delta=2.000; nested_vs_flat32_log2_delta=1.000; NO_POSITION K=50 acc=0.02.
  MEASURED@data/exp_exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7/metrics.json
- v3 selftest seed_7 CPU: SELFTEST_OK; fhrr_unbind_self_inverse_max_diff=1.33e-07; noise_discipline K=50 acc=0.033.
  MEASURED@data/exp_theta_gamma_v3_N16384_gpu_seed_7/metrics.json (2026-07-01 selftest)
- N_DIM=16384: per task-prompt spec.
  CITED@task-prompt (Director spawn 2026-07-01)
- HP_LOG2_SEPARATION_FHRR_VS_CYCLIC=1.5: per task-prompt spec.
  CITED@task-prompt (Director spawn 2026-07-01)
- K_SEQ_FULL max=5000: cell-author choice to extend v2's K=2000 by 2.5x to
  capture cliff at 4x N; NESTED cliff predicted ~K=400-500 with headroom
  through K=5000. HYPOTHESIZED@this prereg.
- CPU smoke wall estimate ~30-40 min: scaled from v2 seed_7 CPU smoke wall
  (57.7s at N=4096) by (16384/4096)^~1.5 ~ 8x. HYPOTHESIZED@this prereg.

## Cardinality_ok (META_RULE_H)

```
EXPECTED_N_UNITS_FULL = 5 arms * 7 K_SEQ = 35
EXPECTED_N_UNITS_SMOKE = 5 arms * 4 K_SEQ = 20
cardinality_ok: bool field in metrics.json
HARD_FAIL_CARDINALITY_BREACH on mismatch
```

## Dispatch info

- Per-seed timeout: **3600s** (per task-prompt; 60x headroom over expected
  GPU wall ~30-60s per seed for 35 pts at N=16384)
- 3 seeds dispatched separately (chunked per USER 2026-06-28)
- Routing: `overnight_queue` (PROT-020 `import torch` confirmed)
- Helper modules on remote (already synced with v2):
  - `experiments/_seed_checkpoint.py`
  - `experiments/_substrate_theta_gamma_v3_N16384_gpu_core.py` (NEW; needs sync)
- run_mode=full verification post-dispatch (§16): mandatory; sentinel file
  size > 5KB at full

## Composes with substrate phase diagram axes

- **Axis I (Sequence encoding) — N-scale extension:** v3 verifies FHRR
  phase-mul + nested-theta*gamma sequence-encoding survives 4x N_DIM
- **Axis J (Order binding) — N-scale extension:** v3 verifies phase-mul
  binding preserves cliff-ordering discriminator at 4x N_DIM

If HARD_PASS at FULL: mechanism proven "N-scale robust" at N in {4096, 16384};
axis I/J promoted from "1-of-4-6 primitives CG at single-N" to
"N-scale-robust CG at 4x range."

## Open questions for landed-VET (Skunkworks)

- Does cliff-K ratio scale linearly with N as expected (v2 CYCLIC=200 ->
  v3 CYCLIC~800)? If super-linear or sub-linear, indicates non-JL capacity
  scaling — new phase-diagram observation.
- Does NESTED preserve advantage over FLAT_32 at 4x N? At N=4096, nested
  cliff was 100 vs flat_32=50 (log2 delta 1.0). At N=16384 the delta may
  compress if NESTED saturates its 64-position capacity faster.
- Is `max_fhrr_vs_cyclic_log2_delta >= 1.5` the right floor for higher N?
  If v3 hits ~2.0 again, the threshold is loose; if v3 hits ~1.5, threshold
  is calibrated correctly.
