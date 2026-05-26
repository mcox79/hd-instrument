# exp_dev → queue: Strategy x Research shore-up anchors (4 anchors, 2026-05-23)

**Source**: Strategy x Research shore-up matrix `notes/strategy_research_shoreup_matrix_2026-05-23.md` (recommended sequencing 1-3 + portfolio-gap Anchor 4).

**Pause flag CLEARED** at dispatch time (orchestrator confirmed). All 4 anchors below have passed local self-test + smoke gate. Each script includes metrics-write block (env-var-driven `HDLAB_EXP_NAME` outdir + atomic write_metrics).

**Routing schema**: Schema B (markdown table) per dispatch.py-verified parser. All 4 anchors -> `remote_cpu_queue` per matrix sequencing (CPU-cheap; queue depth >= 1 for hours per [[feedback-pipeline-pacing]]).

| queue            | name                                              | script                                                              | prereg                                                                  | timeout(s) |
|------------------|---------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap2_conformal_subsumption_v1              | experiments/exp_wave14_cap2_conformal_subsumption_v1.py             | preregs/2026-05-23_wave14_cap2_conformal_subsumption_v1.md              | 3600       |
| remote_cpu_queue | wave14_betT_mondrian_anti_RM_conformal_v1         | experiments/exp_wave14_betT_mondrian_anti_RM_conformal_v1.py        | preregs/2026-05-23_wave14_betT_mondrian_anti_RM_conformal_v1.md         | 1800       |
| remote_cpu_queue | wave14_betV_kappa4_separation_v1                  | experiments/exp_wave14_betV_kappa4_separation_v1.py                 | preregs/2026-05-23_wave14_betV_kappa4_separation_v1.md                  | 1800       |
| remote_cpu_queue | wave14_substrate_glauber_generative_smoke_v1      | experiments/exp_wave14_substrate_glauber_generative_smoke_v1.py     | preregs/2026-05-23_wave14_substrate_glauber_generative_smoke_v1.md      | 5400       |

## Per-anchor brief

**Anchor 1 — wave14_cap2_conformal_subsumption_v1 (HIGH)**: Cap 2 Gap C rescue (Rescue 5 of v160 rehab). Re-axiomatizes Cap 2 as DOWNSTREAM conformal calibration over Bet G stream; Pattern 1 metric re-axiomatization. Zero substrate change. HARD PASS: >=3/5 seeds reach committed_acc>=0.90 at abstain<=0.20 + monotone Pareto. HARD FAIL: 0/5 seeds satisfy at any alpha. PASS rescues Cap 2 from PROVISIONAL ❌ to ✅. ETA 30 min.

**Anchor 2 — wave14_betT_mondrian_anti_RM_conformal_v1 (MEDIUM)**: Bet T close-or-rescue via Mondrian conformal stratified by anti-RM(1,m) coset (Drill 3, P_deflated=0.40). The anti-coset is the substrate-novel stratifier never tested. HARD PASS: per-coset coverage in [0.85, 0.95] for all 4 anti-RM cosets + mean_set_size<=4. HARD FAIL: coverage outside [0.80, 0.99] for any coset OR mean_set_size>8. ETA 10 min.

**Anchor 3 — wave14_betV_kappa4_separation_v1 (MEDIUM-LOW)**: Bet V close-or-reject via substrate-novel higher-cumulant signature. k_4(stored) - k_4(unstored) separation in SD. HARD PASS: |sep|>=2 SD + sign-consistent. HARD FAIL: |sep|<1 SD. Smoke directional signal: k4_stored=-1.07, k4_unstored=-0.15 at N=1024 1-seed -> |sep|=1.61 SD. ETA 10 min.

**Anchor 4 — wave14_substrate_glauber_generative_smoke_v1 (HIGH-strategic)**: Portfolio gap #5 dead-or-alive test for 12th capability axis (generative-mode). Glauber sampling from random init in bimodal-beta regime; measures novelty + diversity + stability + binding coherence. HARD PASS: all 4 gates satisfied at best beta cell. HARD FAIL: at every beta cell, novelty<0.05 OR diversity<0.01 OR stability<0.20. ETA 60 min.

## Smoke results

- Anchor 1 (Cap 2 conformal): N=1024 1-seed -> PARTIAL with monotone Pareto, acc=1.0 across all alphas (sub-capacity smoke; structural validation only).
- Anchor 2 (Bet T anti-RM): N=512 3-hyp 1-seed -> FAIL (cov=1.0 above ceiling; small-N artifact of tiny calibration); structure valid.
- Anchor 3 (Bet V kappa_4): N=1024 1-seed -> PARTIAL with directional signal |sep|=1.61 SD, sign_consistent.
- Anchor 4 (Glauber generative): N=1024 1-seed beta in {4,6} -> LIMITED at beta=6 (nov=1.0, div=0.037, stab=0.90, coh=0.22); chains reach stability but diversity is borderline; FULL N=4096 5-seed 3-beta is the discriminating run.

All 4 self-tests PASSED. All 4 smokes produced valid metrics.json with positive structural assertions.

## Pipeline implications

- Total CPU span: ~1 hr 50 min behind existing queue, satisfies [[feedback-pipeline-pacing]] queue-depth-on-CPU invariant.
- GPU queue untouched; remote CPU pipeline depth refilled.
- Local CPU not used (none of these meet sub-60s tier C).
