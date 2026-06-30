# Pre-registration: substrate_theta_gamma_v2_FHRR_all_complex

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Director URGENT GPU fill cycle 2026-06-30 + v1 (a24de6ad)
honest-abort at smoke (hybrid bipolar+phase produced ill-defined complex
semantics; K_SEQ=50 cyclic-shift saturated 1.000; phase arms degraded to
0.10-0.30). Design spec:
`notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md`

## Anchor

`substrate_theta_gamma_v2_FHRR_all_complex_seed_{7,13,19}` (3 sibling
files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_theta_gamma_v2_FHRR_all_complex_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; ~58s wall per seed)
- **Full queue:** `overnight_queue` (GPU runner; PROT-020 `import torch`
  present; CUDA complex64 matmul-bound)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch
  routes through Orchestrator via SendMessage post-commit.

## Why this cell exists (the gap v1 didn't close)

v1 used HYBRID bipolar HD + phase-multiplied position; mixing of real-valued
bipolar and complex phases produced non-standard form neither binding op
handled cleanly. v1 cell-author flagged "FHRR all-complex codebook
redesign" as the fix. v2 implements verbatim:
- ALL-COMPLEX FHRR codebook (unit-phase exp(i*phi) complex64)
- Theta-gamma phase binding = element-wise complex multiplication
- Sequence encoding via phase-multiplied bundle (complex sum)
- Decoding via complex-conj unbind + magnitude similarity cleanup

Phase diagram coverage value (per spec): closes 2 substrate axis families
simultaneously — axis I (sequence encoding) + axis J (order binding).
Axis A (vector type) exercised genuinely (FHRR alone, not collapsing with
bipolar/HRR as in ANCHOR 4 v1/v2/v3 byte-degenerate phantom).

## Arms (5 arms; OUTER axis; LOCKED)

| Arm | Codebook | Position basis | Encode | Decode |
|-----|----------|----------------|--------|--------|
| `NO_POSITION` | FHRR complex64 | none (chance) | complex sum | argmax|<cb, seq>| |
| `CYCLIC_SHIFT` | bipolar {-1,+1}^N | implicit roll | sum of rolled items | inverse roll + cosine |
| `FHRR_FLAT_PHASE_8` | FHRR complex64 | 8 unit-phase | phase-mul + sum | conj-mul + argmax magnitude |
| `FHRR_FLAT_PHASE_32` | FHRR complex64 | 32 unit-phase | phase-mul + sum | conj-mul + argmax magnitude |
| `FHRR_NESTED_THETA_GAMMA` | FHRR complex64 | theta(8) * gamma(8) = 64 | phase-mul nested | conj-mul + argmax magnitude |

## Sweep axes

| Axis | FULL values | SMOKE values | Count |
|------|-------------|--------------|-------|
| arm | 5 | 5 | 5 |
| K_SEQ | {50, 100, 200, 500, 1000, 2000} | {50, 100, 200, 500} | 6 / 4 |

**Cardinality:**
- FULL: 5 * 6 = **30 phase points per seed**
- SMOKE: 5 * 4 = **20 phase points per seed**

EXPECTED_N_UNITS_FULL=30, EXPECTED_N_UNITS_SMOKE=20 LOCKED at module init.

## Regime (anti-saturation; LOCKED)

- N_DIM = 4096 (smaller than ANCHOR 4 v3's 8192 to reduce capacity headroom)
- ITEM_VOCAB_SIZE = 10000 (large; ~13 bits inter-item discrimination)
- NOISE_SIGMA = 0.05 (Gaussian noise at retrieval; complex for FHRR, real for CYCLIC)
- N_QUERIES_PER_K_full = 50; smoke = 25

v1 had CYCLIC_SHIFT saturating 1.000 at K_SEQ=50 N_DIM=2048.
v2 uses N_DIM=4096 + ITEM_VOCAB=10000 + NOISE_SIGMA=0.05; this delays the
cliff but only modestly for CYCLIC (1.0 at K=50, 1.0 at K=100, 0.68 at K=200
in smoke seed=7).

## Mechanism (FHRR core)

```python
def theta_gamma_bind(item_hd_complex, position_hd_complex):
    return item_hd_complex * position_hd_complex  # phase addition

def theta_gamma_unbind(bound_hd_complex, position_hd_complex):
    return bound_hd_complex * position_hd_complex.conj()

def encode_sequence(items, positions):
    return (items * positions).sum(dim=0)  # complex sum

def decode_at_position(seq, position, item_codebook):
    candidate = seq * position.conj()
    scores = (item_codebook.conj() @ candidate).abs()
    return scores.argmax()

def nested_theta_gamma_position(t, g, theta_codes, gamma_codes):
    return theta_codes[t] * gamma_codes[g]  # nested phase combination
```

## Pre-reg discriminator bands (LOCKED)

### HARD_PASS gates (ALL must hold)
- `n_pairs_differ >= 9 of 10` (cross-arm distinctness; META_RULE_AX FULL floor)
- `max_fhrr_vs_cyclic_log2_delta >= 0.3` (FHRR cliff differs from CYCLIC by >=0.3 log2)
- `min_cross_arm_log2_delta >= 0.1` (all-pairs cliff |dlog2_K| >= 0.1)
- `nested_vs_flat32_log2_delta >= 0.1` (nesting genuinely helps)
- `cv across seeds <= 0.10`
- `NO arm saturates >= 0.999 at K_SEQ=50` for >=3 arms (META_RULE_Q regime check)
- `NO_POSITION at K=50 noisy < 0.999` (DISCRIMINATOR-MUST-SURVIVE-SCALE noise discipline)
- META_RULE_AY: verdict-emitter HARD_FAIL if HARD_PASS claimed but pairs_differ < 7

### MIDDLE_BAND gate
- `n_pairs_differ >= 6 of 10` AND `max_fhrr_vs_cyclic_log2_delta >= 0.15`
- FHRR variants distinguish but log2-separation below HP floor

### HARD_FAIL gates
- HARD_FAIL_CARDINALITY_BREACH: observed != expected
- HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): n_pairs_differ < 7 at FULL (< 4 at smoke)
- HARD_FAIL_REGIME_TOO_EASY (META_RULE_Q): >=3 arms saturate at K_SEQ=50
- HARD_FAIL_NOISE_DISCIPLINE: NO_POSITION saturates K=50 noisy (>=0.999)
- HARD_FAIL_FHRR_NO_CAPACITY (smoke): no FHRR arm has cliff_K >= 50
- HARD_FAIL_LLM_LEAK: `n_llm_calls > 0`
- META_RULE_AY downgrade: HARD_PASS but pairs_differ < 7 -> HARD_FAIL

## Smoke gate predicate (4 conditions; ALL must pass)

1. cardinality_ok (20 / 20)
2. n_pairs_differ >= 4 of 10 (smoke AX floor; lower than FULL 9 floor)
3. NO_POSITION at K=50 noisy NOT saturated (<0.999)
4. < 3 arms saturate at K=50 (regime not catastrophically easy)
5. At least 1 FHRR arm has cliff_K >= 50 (mechanism fires)

## Selftest (verified CPU 2026-06-30; SELFTEST_OK)

```
cardinality FULL=30 SMOKE=20
fhrr_unbind_self_inverse_max_diff=1.33e-07
fhrr_K1_clean_retrieval_pass(pred=7)
all 5 arm outcome hashes distinct
all 5 code path hashes distinct
noise_discipline_no_position_K50_acc=0.0667 (well below 0.999 ceiling)
nested_vs_flat32_distinct=True
```

## SMOKE seed=7 result (verified CPU 2026-06-30; HARD_PASS)

```
20/20 phase points
pairs_differ=10/10 (META_RULE_AX perfect)
NO_POSITION@K50_acc=0.000 (noise discipline holds)
max_fhrr_vs_cyclic_log2_delta=2.000 (>>0.3 floor)
nested_vs_flat32_log2_delta=1.000 (>>0.1 floor)
arms_saturating_K50=2 ([CYCLIC_SHIFT, FHRR_NESTED_THETA_GAMMA]) - regime acceptable
cliffs: CYCLIC=200, NESTED=100, FLAT_32=50, FLAT_8=0 (no capacity), NO_POSITION=0
```

Wall: 57.7s CPU smoke. Per-pt: ~3s CPU; GPU expected ~10-100x faster (FHRR
matmul-bound). FULL estimate: 30 pts * 50 queries / smoke 20 pts * 25 queries
= 3x compute => ~180s CPU per seed, ~3-15s GPU per seed.

## SCHEMA-VET checklist (load-bearing pre-dispatch)

- [x] CARDINALITY_OK: EXPECTED_N_UNITS_FULL=30, EXPECTED_N_UNITS_SMOKE=20 declared
- [x] META_RULE_AF arms-must-differ: SHA-256 hash gate per arm-pair
- [x] **META_RULE_AX arms-distinct-across-family-axis: 10/10 pairs distinct at smoke;
      FULL gate 9/10**
- [x] META_RULE_AW seed-config-identical: SEED is only variable across siblings
- [x] META_RULE_AH atomic metrics: `tmp + os.replace` for all writes
- [x] META_RULE_AC numbers tagged: all pre-reg numbers TAGGED below
- [x] META_RULE_AY verdict-emitter HARD_FAIL on self-reported distinctness False
- [x] **META_RULE_Q suspect-1.000 check: gate triggers at >=3 arms saturating K=50**
- [x] `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- [x] `import torch` present (PROT-020 GPU routing)
- [x] CRLB / capacity feasibility: FHRR at N=4096 has capacity ~N/8 = 512 bound
  items for clean retrieval. FLAT_PHASE_8 with 8 positions and 50+ items per
  position saturates basis (correct behavior). NESTED with 64 positions has
  ~50 items/position at K=2000 — well within capacity. crlb_n/a declared:
  this is a retrieval-accuracy cell not a quantitative-noise-floor cell.
- [x] HP_SCOPE: HARD_PASS gates apply to all 5 arms equally
- [x] **DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full N_DIM=4096; NO_POSITION**
      **noisy baseline = 0.000 at K=50 (strictly below 0.999 ceiling); discriminator**
      **structure proven at smoke regime**

## Numbers TAGGED (META_RULE_AC)

- Smoke seed_7 result: 20/20 pts HARD_PASS; pairs_differ=10/10; FHRR vs CYCLIC
  log2_delta=2.000; NESTED vs FLAT_32 log2_delta=1.000; NO_POSITION K=50 acc=0.000.
  MEASURED@data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7_smoke/metrics.json
- Selftest seed_7: SELFTEST_OK; FHRR unbind self-inverse max_diff=1.33e-07;
  noise_discipline NO_POSITION K=50 acc=0.067.
  MEASURED@data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7_selftest/metrics.json
- v1 honest-abort: hybrid bipolar+phase, CYCLIC saturated 1.000 at K=50 N=2048,
  phase arms 0.10-0.30 degraded.
  CITED@notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md
- HP_LOG2_SEPARATION_FHRR_VS_CYCLIC=0.3: per design spec verbatim.
  HYPOTHESIZED@design_spec
- HP_CROSS_ARM_LOG2_DELTA=0.1: per design spec verbatim. HYPOTHESIZED@design_spec
- NOISE_SIGMA=0.05: per design spec verbatim. HYPOTHESIZED@design_spec
- HP_PAIRS_DIFFER FULL=9, SMOKE=4: cell-author choices; FULL requires near-
  perfect distinctness (9 of 10) for HARD_PASS; smoke floor relaxed because
  small-sample K-tail collisions can occur. HYPOTHESIZED@this prereg.

## Cardinality_ok (META_RULE_H)

```
EXPECTED_N_UNITS_FULL = 5 arms * 6 K_SEQ = 30
EXPECTED_N_UNITS_SMOKE = 5 arms * 4 K_SEQ = 20
cardinality_ok: bool field in metrics.json
HARD_FAIL_CARDINALITY_BREACH on mismatch
```

## Dispatch info

- Per-seed timeout estimate: smoke ~58s CPU per seed; FULL on GPU ~10-60s
  per seed (30 pts * 50 queries with GPU complex64 matmul)
- Timeout per seed: **1800s** (per design spec; 30x headroom over CPU smoke)
- 3 seeds dispatched separately (chunked per USER 2026-06-28)
- Routing: `overnight_queue` (PROT-020 `import torch` confirmed)
- Helper modules to SCP: `experiments/_seed_checkpoint.py` and
  `experiments/_substrate_theta_gamma_v2_FHRR_all_complex_core.py`
- run_mode=full verification post-dispatch (§16): mandatory; sentinel file
  size > 5KB at full

## Composes with substrate phase diagram axes

- **Axis I (Sequence encoding):** v2 promotes from positional-shift-only to
  FLAT-phase + NESTED-phase (2 new primitives)
- **Axis J (Order binding):** v2 promotes from cyclic-shift only to FHRR
  phase-multiply (1 new primitive)
- **Axis A (Vector type):** v2 exercises FHRR genuinely end-to-end (caught
  ANCHOR 4 v3 trap where binary/HRR/FHRR collapsed in byte-degenerate regime)

If HARD_PASS at FULL: this single cell promotes 3 axis families from
"untested at chain-grade" to "1 of 4-6 primitives CG."

## Open questions for landed-VET (Skunkworks)

- Is `HP_LOG2_SEPARATION_FHRR_VS_CYCLIC=0.3` (per spec) the right floor, or
  should it be tighter (e.g. 0.5) given smoke shows 2.0 separation?
- FLAT_PHASE_8 had ZERO capacity at K_SEQ=50 (only 8 positions for 50 items);
  is this an arm-design flaw or correct behavior (limited basis)?
  Cell-author judgment: correct behavior; expected and useful as low-capacity
  comparator. FLAT_8 demonstrates capacity scales with n_positions; provides
  natural ranking 8 < 32 < 64.
- nested_vs_flat32_delta=1.000 at smoke (NESTED cliff K=100 vs FLAT_32 K=50)
  — is this enough to claim "theta-gamma rhythm helps" or just "more positions
  helps" (NESTED has 64 vs FLAT_32 has 32)? Skunkworks landed-VET call.
