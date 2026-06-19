# Pre-reg: Crooks forensic erase audit (Strategy 10:03 v151 P1 — COMMERCIAL WEDGE Class 1)

Anti-Hebbian erase audit via empirical entropy difference. Baseline retrieval entropy H_baseline, after insert H_insert, after erase H_erase. delta_S_emp = |H_erase - H_baseline|. N=16384, M_base=200, n_trials=50.

## Verdicts
- `CROOKS_ERASE_VERIFIED` — delta_S_emp < 0.05 (verifiable forensic erase per Crooks FT bound).
- `CROOKS_PARTIAL` — 0.05 <= delta_S_emp <= 0.5.
- `CROOKS_FAILED` — delta_S_emp > 0.5.
