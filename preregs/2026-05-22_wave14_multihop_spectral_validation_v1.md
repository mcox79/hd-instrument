# Pre-reg: Wave 14 Multi-hop Spectral Validation v1

**Filed:** 2026-05-22
**Source:** `research_multihop_chain_rehabilitation_N65536_2026-05-22.md` (Research 18:58 EDT) — section "Spectral validation test".

## Question

Does the top-K eigenvalue span of substrate's W matrix cluster more tightly at large N, directly validating Research's signal-eigenvalue-near-degeneracy mechanism diagnosis?

Research's quantitative prediction:
- N=4096 K=100: top-K eigenvalue span > 0.03
- N=65536 K=100: top-K eigenvalue span < 0.01
- Monotone clustering with N.

## Hypothesis

H_confirmed: spans decrease monotonically AND span(N=65536) < 0.01. Mechanism diagnosis ratified — substrate's deep-chain failure at large N is signal-subspace drift caused by eigenvalue near-degeneracy.

H_falsified: spans don't cluster — Research's primary mechanism wrong; investigate alternative.

## Pre-declared verdicts

- `SPECTRAL_DEGENERACY_CONFIRMED` — monotone clustering AND span(N=65536) < 0.01.
- `SPECTRAL_FLAT` — not monotone OR span(N=65536) ≥ 0.01.
- `SPECTRAL_INCONCLUSIVE` — <2 N values measured.

## Method

For each N ∈ {4096, 16384, 65536}:
1. Build K=100 stored triples T = sign(entity[s] · relation[r] · entity[o]).
2. W = T^T @ T / N.
3. `eigvalsh(W)`; sort descending; take top K.
4. Span = top_K[0] − top_K[K-1].

## Acceptance thresholds

- 0.01 N=65536 threshold per Research's quantitative prediction.
- 0.03 N=4096 threshold (reference baseline).

## Config

- N_grid full: [4096, 16384, 65536].
- K=100, num_entities=200, num_relations=20.
- Single seed=17.
- Smoke: N=[1024, 2048].

## Pre-declared interpretation

- **CONFIRMED**: validates Research's mechanism diagnosis. Direct theoretical support for Resonator rehabilitation (just queued separately). Both diagnostic + therapeutic agree.
- **FLAT**: Research's primary mechanism wrong. Resonator may not restore composition. Investigate alternative diagnoses (Goldstone modes? K-N interaction not captured by spectral analysis?).

## Cost

`eigvalsh(W)` at N=65536: 17GB matrix in fp32 — WON'T FIT at 16GB cap. Use bf16 or fp16. At fp16: ~8.6GB, fits. Total run: <2 min.

## Not in scope

- Random ±1 patterns instead of triple bindings (this measures the substrate's actual chain W).
- Multi-seed (single seed scan).
- K > 100 or K < 100.
