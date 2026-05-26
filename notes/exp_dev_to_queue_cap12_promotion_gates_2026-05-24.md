# exp_dev -> queue: Cap 12 🟢 → ✅ promotion gates + optional third-family hardening (2026-05-24)

**Trigger**: SILENT_IDLE watchdog (GPU=0, CPU=0, 120s idle) at 02:32-ish post-v174 promotion of Cap 12 (composite "AMP-vs-VAMP inference routing infrastructure"). Pipeline emptied unexpectedly — both MP-KS pretest pipeline and interp-family SRHT cross-check landed at-threshold PASS within minutes of each other.

**Pause flag**: ABSENT (verified at dispatch time via `ls data/orchestrator_paused.flag`).

**Routing schema**: Schema B (markdown table). All three anchors -> `remote_cpu_queue` per orchestrator's three-tier policy (CPU-cheap pure-numpy work; queue-depth invariant per [[feedback-pipeline-pacing]]).

| queue            | name                                            | script                                                            | prereg                                                               | timeout(s) |
|------------------|-------------------------------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_mp_ks_pretest_tau_robustness_v1          | experiments/exp_wave14_mp_ks_pretest_tau_robustness_v1.py         | preregs/2026-05-24_wave14_mp_ks_pretest_tau_robustness_v1.md         | 3600       |
| remote_cpu_queue | wave14_interp_family_hadamard_v1                | experiments/exp_wave14_interp_family_hadamard_v1.py               | preregs/2026-05-24_wave14_interp_family_hadamard_v1.md               | 5400       |
| remote_cpu_queue | wave14_interp_family_rm_v1                      | experiments/exp_wave14_interp_family_rm_v1.py                     | preregs/2026-05-24_wave14_interp_family_rm_v1.md                     | 5400       |

## Per-anchor brief

**Anchor 1 — wave14_mp_ks_pretest_tau_robustness_v1 (HIGH, Cap 12 Gate A)**: Same 5 codebooks (iid/SRHT/Hadamard/RM/Kerdock) at N=1024, 5 seeds. For each codebook compute MP-KS once + AMP/VAMP once -> establish empirical truth label. At each tau in {0.15, 0.20, 0.25}: route_from_ks(ks_mean, tau) -> per-tau correct count. **HARD PASS**: >=4/5 correct at EACH tau. **HARD FAIL**: <3/5 at ANY tau. **MIDDLE BAND**: 3-4/5 at one or two tau values. ETA ~30 min.

**Anchor 2 — wave14_interp_family_hadamard_v1 (HIGH, Cap 12 Gate B)**: Reuses the v174 SRHT cross-check design but interpolates G -> Hadamard (no D, no S, vs. SRHT's D and S). 5 alpha cells × 5 seeds × N=1024. **HARD PASS**: Spearman rho >= 0.70 AND max VAMP rel-err < 0.10. **HARD FAIL**: rho < 0.50 OR max VAMP rel-err > 0.20. **MIDDLE BAND**: rho in [0.50, 0.70) or VAMP in [0.10, 0.20). ETA 30-60 min.

**Anchor 3 — wave14_interp_family_rm_v1 (MEDIUM, optional third-family hardening)**: Same design as Anchor 2 but interpolates G -> RM(1,m) (2N bipolar codewords). Cheap CPU; shipping during idle window per [[feedback-pipeline-pacing]] queue-depth invariant. ETA 30-60 min.

## Smoke results

- Anchor 1: N=64 1-seed 2-codebook -> INCONCLUSIVE via "missing codebooks" branch (expected; smoke is structural validation only — full sweep uses 5 codebooks at N=1024). Self-test 6/6.
- Anchor 2: N=64 1-seed 3-alpha -> KILLED via small-N artifact (rho=0.500 borderline; max VAMP rel-err 0.40 at sub-capacity). Same N=64 pattern as the SRHT-family smoke that subsequently PASSed cleanly at N=1024. Self-test 8/8.
- Anchor 3: N=64 1-seed 3-alpha -> KILLED via small-N artifact (same pattern). Self-test 6/6.

All three include the stdout-reconfigure block + env-var-driven HDLAB_EXP_NAME outdir + atomic write_metrics. Remote-side `--self-test` gates passed in 2.6s / 3.2s / 3.6s respectively.

## Pipeline implications

- Remote CPU queue depth: 3 pending after this dispatch (depth =>1 invariant satisfied through ~90-150 min).
- GPU queue: untouched.
- Local CPU queue: untouched (dead per [[project-cpu-resource-underutilized]]).
- Smoke pre-test gate caught the small-N artifact pattern that the SRHT-family v174 PASS also passed through; this is expected and structurally documented.

## Silent verdicts surfaced

None. Most-recently-mentioned silently-landed candidate experiments (Haar-vs-Kerdock cumulant_dichotomy, kerdock_mub_distinguishability, rsb_exchange_mcmc, amp_se_kerdock_longiter) all have only smoke outputs in `data/exp_*_smoke/`; no full-run metrics.json files have landed without verdict events. The most recent verdicts in the status log are the two that triggered this dispatch (MP_KS_PRETEST_PIPELINE_PASS and INTERP_FAMILY_SRHT_PASS at 02:29:19 -04:00) plus the kerdock_2design_v3_stim PASS at 02:19:32. No verdict_handler rescue dispatch is needed.

## Honest framing per [[feedback-no-smoke]]

These are infrastructure-class hardening gates, not substrate-physics novelty. Even a clean three-anchor PASS only:
1. Confirms tau=0.20 is a robust threshold (not fragile artifact) — Gate A.
2. Extends the kappa_n explainer to a third family (Hadamard) — Gate B.
3. Adds a fourth family (RM) — optional breadth.

The v174 rho-degradation pattern (Kerdock 0.900 → SRHT 0.700) is REAL family-specificity weakening. Anchor 2 (Hadamard) is the load-bearing test for Cap 12 ✅ promotion. Anchor 3 is breadth-padding worth running in idle CPU time.

## PROT compliance

- Pause flag CLEARED (verified pre-dispatch).
- All three scripts include `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top.
- All three preregs include verbatim HARD PASS / HARD FAIL / MIDDLE BAND bands per [[feedback-envelope-expansion-fail-bands]].
- Formula self-test cells per [[feedback-strategy-spec-formula-selftests]]: 6+8+6 = 20 cells.
- Background execution per [[feedback-no-blocking-runs]].
- 3 status_log entries written (HIGH x2 for Gates A+B; MEDIUM for optional Anchor 3).
- Decision log appended via `tools/orchestrator/append_decision_log.py`.
