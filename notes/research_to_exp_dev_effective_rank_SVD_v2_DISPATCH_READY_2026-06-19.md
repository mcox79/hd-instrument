# RESEARCH (Director) -> Exp-Dev: effective-rank-SVD v2 DISPATCH-READY (Skunkworks CONFIRMED with band-contradiction fix; HARD_PASS gates on capacity-d_eff correlation only).

(Filename has to_exp_dev per refined cap.)

## Source
- `research_to_skunkworks_PREREG_effective_rank_SVD_pull_up_v2_2026-06-19.md` (commit 1b6ed9c2); Skunkworks v2 confirm landed

## Cell-build summary
- **Encoders:** all-MiniLM-L6-v2 + all-mpnet-base-v2 + bge-large-en-v1.5 + Pythia 2.8B hidden states (4 encoders)
- **3 d_eff methodologies:** participation_ratio + rank95 + spectral_entropy (cross-method consistency check)
- **Capacity sweep per encoder:** standard fact-bank task at recall threshold 0.99
- **n_seeds=5**
- ~20-30 GPU runs; BATCH with Pythia-KV (shared Pythia 2.8B load amortizes)

## Bands (LOCKED v2)
- HARD_PASS gates ONLY on capacity-d_eff Spearman ρ ≥ 0.80 + methodology consistent ±20% + seeds reproduce
- d_eff magnitudes REPORTED as measurements (no pass/fail gate on magnitude); Pythia high or low d_eff both informative

## Standing
Build at your bandwidth; batch with Pythia-KV.

-- Research (Director)
