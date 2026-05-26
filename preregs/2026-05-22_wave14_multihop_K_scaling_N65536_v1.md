# Pre-reg: Wave 14 Multi-hop K-scaling at N=65536 v1

**Filed:** 2026-05-22
**Source:** `research_multihop_chain_rehabilitation_N65536_2026-05-22.md` (Research 18:58 EDT) — falsifiability test #2 (K-scaling).

## Question

At N=65536 with standard per-hop argmax cleanup, does acc_50hop improve monotonically as K decreases from 100 → 50 → 25, as Research's near-degeneracy mechanism predicts?

Research's quantitative predictions:
- K=100: acc_50hop ≈ 0.22 (cycle 121 baseline)
- K=50: acc_50hop ≈ 0.65-0.80
- K=25: acc_50hop ≈ 0.80-0.90

Falsification: if K=50 doesn't significantly improve over K=100, the eigenvalue-degeneracy hypothesis is WRONG.

## Hypothesis

H_confirms: K=25 acc_50hop ≥ 0.70 AND K=50 acc_50hop ≥ 0.50. Smaller K reduces signal-subspace crowding; less per-hop drift.

H_falsifies: K=50 acc_50hop < 0.35 — smaller K doesn't help; mechanism diagnosis wrong.

## Pre-declared verdicts

- `KSCALE_CONFIRMS` — K=25 ≥ 0.70 AND K=50 ≥ 0.50.
- `KSCALE_PARTIAL` — K=50 in [0.35, 0.50].
- `KSCALE_FALSIFIES` — K=50 < 0.35.
- `KSCALE_INCONCLUSIVE` — metric collection error.

## Method

For each K ∈ {25, 50, 100} at N=65536:
1. Build M = sign(Σ K triples) factbase.
2. Run 30 trials × 2 seeds chain queries at depth=50.
3. Per-hop argmax cleanup.
4. Report acc_50hop = mean recovery accuracy at depth 50.

## Acceptance thresholds

Match Research's predictions:
- K=25 PASS: ≥ 0.70 (predicted 0.80-0.90).
- K=50 PASS: ≥ 0.50 (predicted 0.65-0.80).
- K=50 FALSIFICATION: < 0.35.

## Config

- N=8192 smoke, 65536 full.
- K_grid full: [25, 50, 100].
- depth=50 full (25 smoke).
- 30 trials × 2 seeds.

## Pre-declared interpretation

- **CONFIRMS**: signal-eigenvalue near-degeneracy mechanism CROSS-VALIDATED via capability test. Two independent diagnostics agree (this test + spectral validation). Resonator rehabilitation theoretically grounded.
- **PARTIAL**: mechanism partially right; K reduces crowding but not dominantly.
- **FALSIFIES**: Research's near-degeneracy diagnosis is WRONG. Alternative mechanism needed (Goldstone modes? Codebook geometry? Other).

## Cost

argmax chain at N=65536 is fast (no W matrix, just bundle M of size N). 30 trials × 50 hops × 200 cleanup ops × 3 K values × 2 seeds = manageable; ~5-15 min total.

## Not in scope

- Resonator cleanup (separate experiment).
- N-scaling intermediate test (Research's H#3).
- K > 100.
