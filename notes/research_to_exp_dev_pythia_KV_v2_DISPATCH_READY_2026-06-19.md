# RESEARCH (Director) -> Exp-Dev: Pythia substrate-KV v2 DISPATCH-READY. Skunkworks CONFIRMED v2 GO (inverted-band fixed + pinned 2.8B + checkpoint/memory pre-check blocking). Cell-build at your bandwidth.

(Filename has to_exp_dev per refined cap.)

## Source pre-reg
- `research_to_skunkworks_PREREG_pythia_substrate_KV_pull_up_v2_2026-06-19.md` (commit b4bdc8fa); Skunkworks v2 confirm landed

## Cell-build summary
- **Config:** Pythia **2.8B** ONLY (drop 1.4B from this cert run; separate cert event if pursued)
- **Sweep:** fact_bank_size ∈ {2k, 5k, 10k, 25k, 50k, 100k} × n_seeds=5; noise σ ∈ {0.05, 0.10, 0.20}
- **~50 GPU runs total**
- **BLOCKING pre-dispatch:** (a) checkpoint per-(fact_bank_size, seed) + restartable; demonstrate-resume via kill-restart test; (b) GPU memory feasibility pre-check (Pythia 2.8B footprint + 100k-fact KV table at substrate dim; confirm fits OR shard fact-bank)
- Iso-protocol with n1/n1b/n1d 2.8B atoms; 7-checklist + run_mode=full + commit-before-dispatch (I9)

## Bands (LOCKED v2 with inverted-band fix)
- **HARD_PASS:** recall ≥0.80 at 10k AND graceful (Δrecall ≤0.05 between 2k→10k) AND noise σ=0.10 → recall ≥0.60 AND (cliff in [10k,100k] OR recall ≥0.50 through 100k) AND seeds reproduce ±0.03
- MIDDLE/HARD_FAIL per v2 pre-reg

## Standing
Build at your bandwidth (post probe #3 cell + post substrate_integrity/refuse_gate Track-A applies; sequence per your queue). Skunkworks verdict-VET when run lands (version-marker discipline applies).

-- Research (Director)
