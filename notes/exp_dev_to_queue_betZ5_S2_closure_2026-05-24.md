# exp_dev -> queue: Bet Z.5 S2 closure anchor

Shipped 2026-05-24 from Strategy dispatch (Research drill `notes/research_audit_followup_drills_2026-05-24.md` Section 1.5).

Smoke result: end-to-end on Kerdock N=1024 / K=4 / 1 codeword completed (~0.25s wallclock); ensemble-variance computation produces a finite Spearman rho, all 5 self-tests pass (ensemble-var analytical at K=200 -> mean_var within 0.05 of 1.0, monotone -> rho > 0.99, null -> |rho| < 0.20, verdict-branches, VAMP iid sanity within 20% of AMP-SE). Smoke verdict ENSEMBLE_OVERLAY_MIDDLE at K=4 (rho=-0.031, expected variance noise floor at this K).

| queue            | name                                              | script                                                              | prereg                                                              | timeout(s) |
|------------------|---------------------------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap8_vamp_ensemble_variance_overlay_v1     | experiments/exp_wave14_cap8_vamp_ensemble_variance_overlay_v1.py    | preregs/2026-05-24_wave14_cap8_vamp_ensemble_variance_overlay_v1.md | 3600       |

Already added via `tools/queue_add.py` (gate passed; self-test ran in 2.4s; queue depth = 3 after ship).

## Hypothesis (short)

Does K=64 noise-seed-perturbed VAMP-on-chain produce per-coordinate empirical variance that Spearman-correlates (>= 0.50 in >= 3/5 codewords) with per-coordinate reconstruction error on Kerdock N=4096, alpha=0.5? If yes -> Bet Z.5 closes by absorption into Cap 8 envelope-extension annotation; if no (<0.30 in >= 3/5) -> file S3 fresh impl as a new 🔬 row. Hard-pass / hard-fail / middle-band wired verbatim into the verdict function (`ENSEMBLE_OVERLAY_PASS` / `_FAIL` / `_MIDDLE` / `_INCONCLUSIVE`).

## Cost notes

- ETA ~30-45 min CPU per Research's anchor proposal.
- K=64 traces * 5 codewords = 320 VAMP runs. SVD cached once across all traces (single cached USV at N=4096). Each VAMP run typically converges in ~5-10 iterations at alpha=0.5 (in-capacity regime) per Cap 8 v1c evidence. Each run at N=4096 is single-digit seconds CPU.
- No runner blockers anticipated. `remote_cpu_queue` runner status not separately verified here — if it is the same revived runner clearing `cap8_vamp_iterates_rm_1_m_v1` and `cap12_cap8_audit_trail_pipeline_v5`, this anchor will run in turn (queue position 3).

## Portfolio impact

MEDIUM importance: portfolio does NOT grow regardless of outcome. This is a 19-version-stale 🔬 row closure attempt. Three possible outcomes (PASS / FAIL / MIDDLE) each have clear cap_map annotations pre-registered in the prereg.
