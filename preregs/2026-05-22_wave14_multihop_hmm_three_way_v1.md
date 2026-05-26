# Pre-reg: Wave 14 Multi-hop HMM Three-Way Test v1

**Filed:** 2026-05-22
**Source:** `research_multihop_mechanism_3rd_attempt_2026-05-22.md` (Research 20:23 EDT) — Falsifiability Test 1 (most discriminating).

## Question

Do three chain-readout methods at N=65536, K=100, d=50 produce the information ordering predicted by Research's HMM/BCJR framework: hard < soft-forward < full-smoother?

Research quantitative predictions:
- hard Viterbi: acc ~ 0.22 (matches cycle 121 baseline)
- soft-forward-only: acc ∈ [0.5, 0.95]
- full smoother (BCJR): acc ~ 1.000 (matches cycle 127 VAMP-on-chain PERFECT)

## Hypothesis

H_confirmed: hard ≤ 0.30 AND soft ∈ [0.40, 0.95] AND smoother ≥ 0.70 AND ordering monotone — substrate IS an HMM as Research's 3rd-attempt diagnosis claims.

H_refuted: soft ≈ hard OR soft ≈ smoother — soft-forward provides either zero gain or all the gain; HMM framework wrong.

## Pre-declared verdicts

- `HMM_CONFIRMED` — all 3 bands match + monotone ordering.
- `HMM_PARTIAL` — monotone but tighter bands.
- `HMM_REFUTED` — soft ≈ hard OR soft ≈ smoother.
- `HMM_INCONCLUSIVE` — non-monotone or unclear.

## Method

Per trial at d=50, N=65536, K=100:
1. **Hard Viterbi**: standard per-hop argmax cleanup (cycle 121 baseline).
2. **Soft-forward-only**: per-hop softmax posterior → expectation-weighted state for next probe; no backward pass.
3. **Full smoother (BCJR)**: VAMP-on-chain forward-backward EP from cycle 127.

30 trials × 2 seeds. Compare same chain instances across all 3 methods.

## Acceptance thresholds

- 0.30 hard ceiling: matches cycle 121 KILLED.
- [0.40, 0.95] soft band: substantial-but-bounded gain over hard.
- 0.70 smoother floor: matches cycle 127 PERFECT.
- Monotone ordering = HMM information-budget ladder.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- depth=50 full (25 smoke).
- n_trials=30, 2 seeds full.

## Pre-declared interpretation

- **CONFIRMED**: substrate-novel "substrate is an HMM" diagnosis validated. Closes 3rd-attempt mechanism investigation with quantitative match. Research's lit-scan-calibration penalty memory framework lands.
- **PARTIAL**: ordering right but margins tight. HMM mostly right; tighter predictions needed.
- **REFUTED**: substrate NOT an HMM as Research framed it. Either soft-forward provides no gain (forward filter doesn't matter; only backward) OR soft-forward provides all the gain (backward irrelevant). Either way Research's 3rd attempt also wrong.

## Cost

3 methods × 30 trials × 2 seeds × 50 hops at N=65536: roughly 3× VAMP-on-chain cycle 127 cost (~30s) = ~2-5 min total.

## Not in scope

- Geometric-scaling falsifiability test (separate experiment).
- Per-hop p_fail measurement (separate experiment).
- Resonator-warmstart-with-backward (separate experiment).
