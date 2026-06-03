# Pre-registration: Q-A3 L=17 and L=18 cross-layer composition ceiling chase

**Date:** 2026-06-02
**Anchors:** `q_a3_l17_cross_layer_composition_v1_n4096`, `q_a3_l18_cross_layer_composition_v1_n4096`
**Queue:** overnight_queue (GPU)
**Trigger:** Q-A3 L=16 HARD_PASS (all 16 levels EXACT-1.0, 5-seed unanimous). Ceiling not yet found.
**Priority:** Candidate A from v349 REFILL (Section 3 Tier 3 Items 12-13 extension).

## Capability question

Does substrate PP-12 cross-layer composition remain EXACT-1.0 beyond L=16? Where does the first degradation occur?

## Prior results

| Level | Verdict |
|---|---|
| L=10 | HARD_PASS, all fids 1.0000 |
| L=12 | HARD_PASS |
| L=15 | HARD_PASS, all fids 1.0000, 5-seed |
| L=16 | HARD_PASS, all 16 levels EXACT-1.0, 5-seed unanimous |

## Pre-registered bands (BOTH anchors; ceiling-push discipline)

### HARD-PASS
All L level fidelities = 1.0000 (>= 0.9999) unanimous (5/5 seeds).
Architecture guarantees: each M per stage halves from M_inner=100 through the hierarchy; all alphas < alpha_c=0.138.
l17_acc (or l18_acc) >= 0.5.

### MIDDLE
Any L_fid in [0.85, 1.0) OR graceful degradation of inner levels.
Indicates ceiling approached but not yet reached.

### HARD-FAIL
Any L_fid < 0.85 OR l17_acc/l18_acc < 0.5.
Ceiling found at this level.

## Outcome plan

- Both L=17 and L=18 HARD_PASS: extend ceiling to L=18+; file L=19 next cycle.
- L=17 HARD_PASS, L=18 MIDDLE/HARD_FAIL: ceiling found at L=18; substrate composition PP-12 row band-lift eligible.
- Both HARD_FAIL: unexpected; diagnose whether M per stage at L=17+ exceeds alpha_c (check M_MID16=2/N_ACTIVE constraint).

## N-suffix binding (PROT-018)

Both scripts: `N = 4096`, `_N_SUFFIX = 4096`. Production N matches anchor name `_n4096`.

## Timeout estimate

Smoke wall for L=16 was approximately 45s (comparable experiment).
- L=17: ceil(1.5 * 45 * (4096/512)^1.0 * (5/2)) = ceil(1.5 * 45 * 8 * 2.5) = ceil(1350) = 1350s -> round up to **1800s**
- L=18: same calculation -> **1800s**

Both well under 14400s. No flag required.

## Dependency verification

- No data dependencies. Script is self-contained.
- Import: `experiments._seed_checkpoint` present in repo.
- GPU: 17x W matrices at N=4096 = ~1139 MB; 18x = ~1206 MB. Both fit in 8GB GPU.
