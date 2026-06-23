# Pre-reg: sparse_engram_allocation_smoke_v1

Date: 2026-06-23
Anchor: `sparse_engram_allocation_smoke_v1`
Cell: `experiments/exp_sparse_engram_allocation_smoke_v1.py`
Queue: `local_cpu_queue` (smoke+full bundled; numpy-only; expected wall < 15 min)

## Motivation (USER triple-leverage 2026-06-23)

Brain analog: only ~1-3% of neurons fire for any stimulus; engram-cell
allocation is COMPETITIVE -- the most-excited neurons get recruited via
CREB/calcineurin excitability gating (Tonegawa 2007+ Cell; Josselyn 2015).
Cerebellar granule cells use K=4-8 mossy-fiber fan-in (Cayco-Gajic 2017;
Litwin-Kumar 2017). Drosophila Kenyon cells use K=6-8.

Hypothesis: sparse competitive allocation should simultaneously give substrate
  (a) higher capacity (sparse codes have less interference; Frady-Sommer 2018
      ~10x more atoms per N_DIM),
  (b) better noise tolerance (sparse codes survive higher sigma; Cayco-Gajic
      2017 K=5 noise-robust),
  (c) emergent clustering (competitive allocation IS the clustering;
      functionally similar atoms compete for the same ensemble -> Tonegawa
      engram pattern -> clusters emerge).

If even one of the three holds at chain-grade strength, sparse codes become a
top-tier substrate primitive. If all three hold, this is the kind of
substrate-only enabler that lifts the cap_map ceiling on capacity + noise +
self-mapping simultaneously.

## Design

5 arms (all on N_DIM=4096, M_MAX=10000 atoms FULL):

- `ARM_DENSE_BASELINE` -- current substrate; full bipolar dense.
- `ARM_SPARSE_K100`   -- 100 nonzero / 4096 (2.5% sparse).
- `ARM_SPARSE_K50`    -- 1.25% sparse.
- `ARM_SPARSE_K20`    -- 0.5% sparse (close to cerebellar K=4-8 ratio).
- `ARM_SPARSE_K10_COMPETITIVE` -- 0.25% sparse + CREB-style competition:
  for each new atom, sample 10 candidate position-sets, score by
  sum-of-abs inner-products against existing W rows, pick lowest-collision.

Per arm we measure:

- (A) cleanup recall@1 over (M, sigma) grid:
      M_SWEEP = [10, 100, 500, 1000, 2500, 5000, 10000]
      sigma   = [0.0, 0.5, 1.0, 1.5, 2.0]
      N_EVAL  = 200 per cell.
- (B) capacity at sigma=1.0 = largest M with recall@1 >= 0.80.
- (C) clustering purity: planted-family atoms (10 families x 20 per family),
      base atom + within-family noise; k-means K=10; modal-family fraction
      (weighted average). Tests whether the arm's atom representation
      preserves family structure under cleanup-style retrieval geometry.

## Pre-reg bands

HARD_PASS (chain-grade-eligible substrate primitive): ARM_SPARSE_K10_COMPETITIVE
achieves ALL THREE:
- noise lift: recall@1 at sigma=1.5, M=M_MAX >= 0.10 (vs dense Shannon-floor ~0.02)
- capacity lift: capacity at sigma=1.0 >= 2.0 * ARM_DENSE_BASELINE.capacity
- clustering lift: purity >= ARM_DENSE_BASELINE.purity + 0.10

HARD_FAIL: ARM_SPARSE_K10_COMPETITIVE
- recall@1 at sigma=1.5 <= ARM_DENSE_BASELINE.noise_recall + 0.01
- AND capacity not lifted
- AND clustering not improved
- OR endpoint-violation: any arm fails sigma=0 M=10 -> recall@1 == 1.000

MIDDLE_BAND: 1 or 2 of the 3 benefits realized (partial mechanism).

## Sanity self-tests (PRE-DISPATCH)

For all 5 arms:
- sigma=0 endpoint: recall@1 == 1.000 (clean cue, perfect cleanup).
- low-load endpoint: M=10, sigma=0 -> recall@1 == 1.000.
- capacity_at_sigma() returns int >= 5 at sigma=0 (sanity, never zero).
- cluster_purity in [0, 1].

These are enforced inline in `_selftest()`; `--self-test` exits 0 iff all hold.

## By-construction-saturation note

Endpoint sanity is BY-CONSTRUCTION-CLEAN: sigma=0 + M=10 must recall@1=1.000
or the arm is broken. The DISCRIMINATING regime is at sigma>=1.0 with
M>=1000 where dense baseline crowding crushes recall. Sparse arms get
their hypothesized lift exactly in that regime; if the smoke shows
sparse merely matches dense at the discriminating regime, this is a
MIDDLE_BAND outcome and the sparse-coding hypothesis is partially
falsified for substrate.

## Implementation

- N_DIM=4096 (FULL), M_MAX=10000, 5 arms, 5 sigmas, 7 M-points; seeds=[7, 17, 23].
- Smoke: N_DIM=512, M_MAX=200, 4 sigmas, 4 M-points; seeds=[7].
- numpy-only (CPU; no torch).
- Per-seed checkpoint via `experiments/_seed_checkpoint`.
- ASCII-only; no emojis; no em-dashes.

## Smoke gate result (PRE-DISPATCH)

Run `HDLAB_EXP_NAME=sparse_engram_allocation_smoke_v1_smoke .venv/Scripts/python.exe
experiments/exp_sparse_engram_allocation_smoke_v1.py --smoke`:

- `[selftest] PASS: all 5 arms sigma=0 M=10 recall=1.000 + capacity sane + clustering sane`
- N_DIM=512, M_MAX=200, seed=7, 4 sigmas, 4 M-points, 5 arms.
- DENSE   : cap@s1.0=200 noise@s1.5=1.000 purity=1.000
- K100    : cap@s1.0=200 noise@s1.5=1.000 purity=0.733
- K50     : cap@s1.0=200 noise@s1.5=0.975 purity=0.633
- K20     : cap@s1.0=200 noise@s1.5=0.650 purity=0.433
- COMP    : cap@s1.0=50  noise@s1.5=0.300 purity=0.633
- elapsed = 0.6s
- verdict = HARD_FAIL_SMOKE (expected at smoke scale per by-construction
  saturation: N_DIM=512/M=200 puts dense well below saturation crowding, so
  dense wins all 3 metrics by default. The DISCRIMINATING regime is FULL at
  N_DIM=4096/M=10000 where dense crowding crushes recall and sparse arms
  get their hypothesized lift. This is the same by-construction pattern
  banked in atom_feature_encoder_smoke_v1.)
- endpoint=True (sigma=0 M=10 -> recall=1.000 for all 5 arms; sanity holds)
- REQUIRED_FIELDS schema PASSED (verdict / verdict_msg / elapsed_s / summary / per_seed)

FULL runtime estimate (post vectorization of competitive scoring):
- Competitive arm dominates: O(M^2 * n_candidates * k) build cost.
- Timed: M=5000 -> 28s, extrapolated M=10000 ~ 112s per seed.
- Other 4 arms: O(M) builds + O(N_EVAL * N_DIM * M) recall grid; ~3 min per seed.
- 3 seeds * (~2 min competitive + ~3 min other arms) ~ 15 min wall.
- Timeout: 1800s (30 min) = 2x safety margin.

## Expected FULL behavior

- If ARM_SPARSE_K10_COMPETITIVE achieves all 3 lifts -> HARD_PASS, promote
  to `hdlab/sparse_competitive_allocator.py` SAME CYCLE, queue capacity
  follow-up at M=100k.
- If 1-2 of 3 lift -> MIDDLE_BAND, characterise WHICH benefit substrate
  realises; queue arm ablation (sparse-without-competition vs
  competition-on-dense) to factor mechanism.
- If 0 of 3 lift -> HARD_FAIL; sparse-coding hypothesis dead for substrate
  at this N_DIM/M scale, route to Research for revival angle (different K?
  different competition rule? superposition recovery via re-sparsification?).

## Self-test command

```
HDLAB_EXP_NAME=sparse_engram_allocation_smoke_v1_smoke .venv/Scripts/python.exe \
  experiments/exp_sparse_engram_allocation_smoke_v1.py --self-test
```
