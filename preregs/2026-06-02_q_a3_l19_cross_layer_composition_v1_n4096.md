# Pre-registration: Q-A3 L=19 cross-layer composition ceiling chase

**Date:** 2026-06-02
**Anchor:** `q_a3_l19_cross_layer_composition_v1_n4096`
**Queue:** overnight_queue (GPU)
**Trigger:** Q-A3 L=17 and L=18 HARD_PASS (both EXACT-1.0 unanimous 5-seed, v351). Ceiling not yet found.
**Priority:** Ceiling chase continuation (next in L-series).

## Capability question

Does substrate PP-12 cross-layer composition remain EXACT-1.0 at L=19? Where does the first degradation occur?

## Prior results

| Level | Verdict |
|---|---|
| L=15 | HARD_PASS, all fids 1.0000 |
| L=16 | HARD_PASS, all 16 fids EXACT-1.0, 5-seed |
| L=17 | HARD_PASS, all 17 fids EXACT-1.0, 5-seed |
| L=18 | HARD_PASS, all 18 fids EXACT-1.0, 5-seed (elapsed=0.54s) |

## Pre-registered bands

### HARD-PASS
All 19 level fidelities >= 0.9999 unanimous (5/5 seeds).
l19_acc >= 0.5.

### MIDDLE
Any L_fid in [0.85, 1.0) OR graceful degradation.
Ceiling approached but not yet hit.

### HARD-FAIL
Any L_fid < 0.85 OR l19_acc < 0.5. Ceiling found at L=19.

## Outcome plan

- HARD_PASS: extend ceiling to L=19+; file L=20 next cycle.
- MIDDLE/HARD_FAIL: ceiling found; PP-12/Q-A3 band-lift tracker L-ceiling condition MET; file strategy note.

## N-suffix binding (PROT-018)

Script: `N = 4096`, `_N_SUFFIX = 4096`. Anchor name `_n4096` matches.

## Timeout estimate

Prior L=17 FULL elapsed=1.30s, L=18 FULL elapsed=0.54s (fast algebraic primitives).
Using L=17 as conservative proxy (1.30s):
timeout = ceil(1.5 * 1.30 * (4096/512)^2.0 * (5/2)) = ceil(1.5 * 1.30 * 64 * 2.5) = ceil(312) = 312s.
PROT-019 floor for _n4096 = **14400s**. Using 14400s.

Local GPU unavailable; script structure verified (import chain + PROT-018 N binding confirmed).
L=17 and L=18 were < 2s FULL; L=19 expected similar.

## Dependency verification

No data dependencies. Script self-contained. Import: `experiments._seed_checkpoint` EXISTS.
GPU memory: 19 W matrices at N=4096 = 19 * 67 MB = 1273 MB. Fits in 8 GB GPU.
