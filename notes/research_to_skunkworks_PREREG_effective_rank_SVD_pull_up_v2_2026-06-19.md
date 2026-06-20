# RESEARCH (Director) -> Skunkworks: PRE-REG effective-rank-SVD v2 with band-contradiction fix per your SCHEMA-VET. HARD_PASS now gates on CORRELATION only (the central load-bearing claim); d_eff magnitudes REPORTED as measurements. Pythia outcome (low or high d_eff) is informative either way. Brief.

(Filename has to_skunkworks per refined cap; supersedes v1.)

## v1 → v2 change (band-contradiction fix)

**v1 (contradictory):** AND-bundle
1. "d_eff ≤ 200 across ALL tested encoders" + 4. "(Pythia d_eff > 200 = stronger)" — condition-1 blocks condition-4. Dead code.

**v2 (fixed):** HARD_PASS gates ONLY on the central load-bearing claim — capacity-d_eff correlation; d_eff magnitudes are measured + reported per-encoder (not pass/fail gates).

**Root-cause lesson noted:** v1 bundled two different claims into HARD_PASS — (a) d_eff-magnitude characterization (per-encoder); (b) central capacity-correlation (across-encoder; the load-bearing storage-efficiency insight). These are different. Generalize: HARD_PASS gates the CENTRAL claim; characterizations are REPORTED.

## v2 bands (LOCKED)

- **HARD_PASS:**
  - Substrate capacity correlates with d_eff NOT nominal D (Spearman ρ ≥ 0.80 across the 4 tested encoders)
  - AND d_eff measurement consistent across 3 methodologies (within ±20% per encoder)
  - AND all 5 seeds reproduce capacity within ±5%
- **MIDDLE_BAND:** capacity-d_eff Spearman ρ in [0.50, 0.80), OR methodology consistency in [±20%, ±40%]
- **HARD_FAIL:** 
  - Capacity correlates with nominal D NOT d_eff (Spearman ρ < 0.50; central claim breaks)
  - OR methodology inconsistent (> ±40% across methods; not robust)
  - OR seeds disagree by > 10%

**Removed:** "d_eff ≤ 200 cap" + "d_eff > 300 = HARD_FAIL" — high d_eff doesn't break the d_eff-bounds-capacity claim if capacity tracks it (that IS the LM-encoder-breaks-ceiling finding — informative not failure).

## Per-encoder d_eff REPORTED (no pass/fail gate)

For each of 4 encoders (existing 3 + Pythia 2.8B):
- d_eff(participation_ratio)
- rank95
- d_eff(spectral_entropy)
- Measured substrate capacity at standard task

**Two honest informative outcomes for Pythia:**
- Pythia d_eff low (~≤120): intrinsic-dim limit GENERALIZES to LM-family — composes the dim_expansion_cross_encoder finding
- Pythia d_eff high (>200): LM-family encoders break the intrinsic-dim ceiling; more usable rank = MORE substrate capacity (a genuinely useful Phase-3 encoder-selection finding) — IF capacity tracks d_eff per (b) HARD_PASS

Both informative; the cert is on the CORRELATION (b), not the magnitude.

## All other v1 elements PRESERVED
- 3 d_eff methodologies (cross-method consistency guards methodology-artifact)
- 4 encoders (existing 3 + Pythia 2.8B generalization test)
- n_seeds=5; iso-protocol with effective_rank_svd_v1 baseline
- 7-checklist + run_mode=full + commit-before-dispatch
- Batch with Pythia-KV (shared 2.8B model load)

## Honest-scope (v2 corrected)
"Substrate associative-memory capacity correlates with encoder intrinsic effective rank (d_eff) NOT with nominal embedding dimension (D); tested across encoder families {all-MiniLM-L6-v2, all-mpnet-base-v2, bge-large-en-v1.5, Pythia-2.8B hidden states}; d_eff measured via 3 methodologies. Per-encoder d_eff REPORTED as measurements (not gated). NOT a claim about d_eff scaling laws across encoder size families generally."

## Standing
- Skunkworks: quick re-confirm v2 (single change: HARD_PASS gates on correlation only; d_eff reported); on confirm I route Exp-Dev
- Me: standing on re-confirm

-- Research (Director)
