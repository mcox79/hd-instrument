# Pre-reg: Wave 14 Bet Z.1 SRHT compressive readout v1

**Filed:** 2026-05-22
**Source:** `research_cued_holistic_readout_primitive_2026-05-22.md` (Research 14:50 EDT)
**Bet:** Bet Z-readout (new), sub-axis Z.1 SRHT compressive readout

## Question

At N=4096 with K=1000 stored bipolar patterns, does Subsampled Randomized Hadamard Transform (Tropp 2011) preserve the top-10 inner-product ranking using M=2000 measurements?

Research's falsifiable prediction: top-10 recall ≥ 90% with M = O(ε⁻² log K) measurements.

## Hypothesis

H_pass: SRHT preserves the top-10 ranking from brute-force O(N·K) inner products. Recovery > 0.90 at M=2000.

H_kill: top-10 recall < 0.70 — JL guarantee broken (possible structured-substrate non-IID correlation).

## Pre-declared verdicts

- `BET_Z1_PASS` — top-10 recall ≥ 0.90 (substrate-novel fast readout viable).
- `BET_Z1_PARTIAL` — 0.70 ≤ recall < 0.90.
- `BET_Z1_KILLED` — recall < 0.70.
- `BET_Z1_INCONCLUSIVE` — metric collection error.

## Method

1. Generate K random bipolar patterns at length N.
2. Build SRHT sketch: S = √(N/M) · H[row_idx] · diag(D), where H = Sylvester-Hadamard, row_idx = M random rows, D = N random signs.
3. Pre-sketch: sketched_patterns = patterns @ S^T → (K, M).
4. **Planted-signal queries**: query = Σ patterns[plant_idx] + 10% noise (n_plant=10 patterns plant per query). Brute-force top-10 should recover the planted indices.
5. Per query: brute-force top-10 (rank by patterns @ query) vs SRHT top-10 (rank by sketched_patterns @ S @ query).
6. top-10 recall = |brute_top10 ∩ srht_top10| / 10.
7. Average across 5 query seeds.

## Acceptance thresholds

- 0.90 recall = Research's falsification threshold.
- 0.70 lower bound = "JL preserves *something* but barely".

## Config

- N=1024 smoke, 4096 full.
- K=100 smoke, 1000 full.
- M=200 smoke, 2000 full.
- top_k=10.
- 1 query seed smoke, 5 query seeds full.

## Pre-declared interpretation

- **PASS**: Bet Z.1 PROMOTED to substrate-product readout primitive. Z.2 C2PO next; Bet Z-readout primitive lane opens (Lane A fast retrieval + Lane D fast cognitive query).
- **PARTIAL**: SRHT works at low load but margin tight; investigate ε / M sensitivity.
- **KILLED**: substrate-structured (Hebbian W) introduces non-IID correlations that break JL. Bet Z.1 closed; pivot to Z.2 only.

## Not in scope

- Q: substrate-coupling via W (this is the pure-pattern readout test; substrate coupling is a follow-up).
- Online speed measurement (we report theoretical speedup; actual wall-time is hardware-specific).
- Z.2 C2PO classical 2-pulse echo (separate experiment).
