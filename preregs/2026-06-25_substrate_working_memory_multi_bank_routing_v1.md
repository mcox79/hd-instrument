# Pre-registration: substrate_working_memory_multi_bank_routing_v1

**Date:** 2026-06-25
**Anchor:** substrate_working_memory_multi_bank_routing_v1
**Queue:** local_cpu_queue
**N:** N_DIM=4096, **Seeds:** [11, 13, 19], **K_TOTAL:** 256 (plus stretch K=1024)

## Scientific question

Does decomposing working memory across multiple W-matrix banks (each within
the per-slot K-ceiling=64 verified by Cell D today), with a routing layer
picking the right bank per slot, lift the total WM capacity past the single-W
ceiling -- the same architectural-decomposition pattern that delivered
chain-grade KG retrieval at M=100k via partition routing today?

Background: USER's frequency-multiplexing idea (Cell Y today,
`exp_substrate_working_memory_frequency_multiplexed_lock_in_v1`) HARD_FAILED
with massive intermod bleed (K=128 bleed=0.180; K=256 bleed=0.453) -- the
4th cell-evidence point that FDM stacking on a shared substrate W produces
crosstalk that eats any per-symbol fidelity gain. The corrected substrate
analog is to give each bank its own W (separate hardware), within the
per-bank K-ceiling verified by Cell D. Brain analog: PFC working memory
uses MULTIPLE cortical microcircuits each holding small K with attention/
routing picking the read bank.

## Pre-registered bands

**HARD-PASS_CHAIN_GRADE_WM_MULTI_BANK_K256:**
- Best MULTI_BANK arm at K_total=256 has mean recall >= 0.95 at sigma=1.0
  (vs NAIVE single-bank K=256 = 0.555 baseline)
- AND cv <= 0.05 across 3 seeds
- AND router accuracy >= 0.95 for slot->bank mapping (else multi-bank can't
  deliver on its promise)

**HARD-PASS_PARTIAL_MULTI_BANK_LIFT:**
- Best MULTI_BANK at K_total=256 lifts recall by >= 0.20 over NAIVE single-bank
  K=256 (= 0.555 baseline), but does not clear absolute 0.95 chain-grade floor
- Still significant evidence the decomposition pattern works at WM

**HARD-PASS_BONUS_K1024:**
- ARM_MULTI_BANK_32x32_K1024 (stretch arm) mean recall >= 0.95 at sigma=1.0
  (would extend substrate-native WM K-ceiling 32x over single-bank)

**MIDDLE:** Lift in [0.05, 0.20] over NAIVE K=256 -- partial mechanism
demonstrated, requires substantial further tuning.

**HARD-FAIL_ROUTER_CROSSTALK:** MULTI_BANK <= NAIVE at K_total=256 (router
selection introduces crosstalk that eats per-bank gain -- honest negative;
would inform that WM extension needs different architectural primitive).

**HARD-FAIL_BANK_SIZE_DEGENERATE:** Only one specific (N_BANKS, K_PER_BANK)
configuration delivers the lift (lacks robustness; suggests artifact rather
than mechanism).

## Sanity rails (must hold or RAIL_SANITY_BREACH)

- ARM_NAIVE_SINGLE_BANK_K32 mean recall ~ 1.000 (cleanup primitive sanity)
- ARM_NAIVE_SINGLE_BANK_K128 mean recall in [0.85, 0.94] (matches Cell D
  NAIVE_K128=0.908 within rail tolerance; META_M6 derivation)
- ARM_NAIVE_SINGLE_BANK_K256 mean recall in [0.51, 0.60] (matches Cell D
  NAIVE_K256=0.555 within rail)

If these rails breach, the comparison is meaningless and the cell must be
re-dispatched after methodology fix (regimes drifted from Cell D today).

## Q-discipline guards (USER MASTER BIAS CHECKLIST 2026-06-24 Q + S)

- If ANY arm hits >= 0.995 saturation at K_total=256, flag BIAS-Q
  (suspect saturation; UNDER-claim tier).
- META_M6 baselines DERIVED from Cell D today's measurements. Per-arm
  metrics reported (Fix #28); verdict reads metrics.json per-arm not just
  verdict_msg summary.
- Smoke-vs-full discipline: smoke MUST match full along N_DIM and K-per-bank
  dimensions (no smoke-vs-full sign-flip per today's 3-cell pattern).
  Smoke runs at N_DIM=4096 (same as full) with reduced N_ITEMS_PER_K and
  single seed only.

## Calibration rationale

Cell D today established Per-Bank K-Ceiling at sigma=1.0:
- NAIVE K=32: 1.000 (chain-grade)
- NAIVE K=64: 1.000 (chain-grade)
- NAIVE K=128: 0.908 (just below 0.95 threshold)
- NAIVE K=256: 0.555 (well below)
- NAIVE K=512: 0.233 (collapsing)

So 8 banks x 32 items each = 256 total (each bank firmly within
chain-grade envelope). 4 x 64 = 256 (each bank at 1.000 boundary). 16 x 16
= 256 (deeply within). 2 x 128 = 256 (degraded; tests whether more bigger
banks beats fewer smaller banks).

Cell 1 partition routing today (chain-grade @ M=1M with part_size=2000)
demonstrated the routing primitive works at large M with clean category
cues (cat_cos=0.70). Same routing math reused here.

## N-suffix section
N_DIM = 4096 (matches Cell D for apples-to-apples comparison).
CODEBOOK_SIZE = 1024 (max K_total across arms).

## Timeout estimate
Cell D today: full run 3 seeds, K-sweep [32,64,128,256,512], 200 items per K,
sigma-sweep [0.0, 0.5, 1.0] = elapsed_s=30.2.

This cell: full run 3 seeds, 7 arms x K-sweep (3-7 K points per arm),
N_ITEMS_PER_K=200, single sigma=1.0 (multi-bank arms; naive rails at sigma=1.0
only too). Each multi-bank arm does N_BANKS cleanup operations per query.
Estimate: per-seed roughly 3x Cell D = ~30s per seed; 3 seeds = ~90s.

Add 8th arm (32x32_K1024): each query inside that arm has K_total=1024
operations; ~10x slower per query but only 200 items, so ~30s extra per
seed = ~90s extra. Total: ~3 minutes wall.

Timeout floor (PROT-019): >=600s.
formula: ceil(1.5 * 30 * (4096/4096)^1.0 * (3/1)) = 135 s
applied floor 600 s.
timeout_s = 600
