# exp_dev -> queue: BBMD Cap-12 rehab top-2 anchors (2026-05-24)

**Source**: Research deep assessment `notes/research_bbmd_cap12_rehab_assessment_2026-05-24.md` recommended top-2 ranked rehab anchors (R3 + R1).

**Pause flag CLEARED** at dispatch time (orchestrator confirmed via direct check on `data/orchestrator_paused.flag`). Both anchors passed local self-test + smoke gate. Both passed remote `--self-test` gate (2.6-2.8s each). Each script includes metrics-write block (env-var-driven `HDLAB_EXP_NAME` outdir + atomic write_metrics).

**Routing schema**: Schema B (markdown table) per dispatch.py-verified parser. Both anchors -> `remote_cpu_queue` per Research recommendation (CPU-cheap; queue depth >= 1 per [[feedback-pipeline-pacing]]).

| queue            | name                                       | script                                                       | prereg                                                          | timeout(s) |
|------------------|--------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_mp_ks_pretest_pipeline_v1           | experiments/exp_wave14_mp_ks_pretest_pipeline_v1.py          | preregs/2026-05-24_wave14_mp_ks_pretest_pipeline_v1.md          | 3600       |
| remote_cpu_queue | wave14_interp_family_cross_check_v1        | experiments/exp_wave14_interp_family_cross_check_v1.py       | preregs/2026-05-24_wave14_interp_family_cross_check_v1.md       | 5400       |

## Per-anchor brief

**Anchor 1 — wave14_mp_ks_pretest_pipeline_v1 (HIGH, R3)**: BBMD Cap-12 rehab R3 (P_deflated=0.55). Operationalizes the v171 negative result (MP-KS already discriminates SRHT 0.59 / Hadamard 0.59 / RM(1,m) 0.34 / Kerdock vs iid Gauss ~0) as an INFRASTRUCTURE-class pre-flight diagnostic: substrate ships a 15ms MP-KS pre-test that routes customer codebooks to AMP-OK or VAMP-required at tau=0.20. Validated on the 5 known codebooks + measures empirical truth via running BOTH AMP and VAMP. HARD PASS: >=4/5 routed correctly AND speedup >=10x. HARD FAIL: <3/5 correct OR speedup <2x. PASS yields infrastructure-class 12th capability candidate; FAIL keeps portfolio at 11 unless Anchor 2 saves it. ETA 15-30 min.

**Anchor 2 — wave14_interp_family_cross_check_v1 (HIGH, R1)**: BBMD Cap-12 rehab R1 (P_deflated=0.30). Tests whether the v170 BBMD_VAMP_CORRESPONDENCE_PASS Spearman rho=0.900 finding generalizes to a non-Kerdock interpolation family (iid-Gauss -> SRHT). Same 5 alpha cells {0, 0.25, 0.5, 0.75, 1.0} as v170, 5 seeds, N=1024. HARD PASS: Spearman rho >= 0.70 AND max VAMP-rel-err < 0.10. HARD FAIL: rho < 0.50 OR max VAMP-rel-err > 0.20. PASS gives cross-family generalization evidence -> META-DIAGNOSTIC capability class. FAIL kills R1 at this family (predictor is Kerdock-internal). ETA 30-60 min.

## Smoke results

- Anchor 1: N=64 1-seed 2-codebook (iid + SRHT) -> INCONCLUSIVE via "missing codebooks" branch (expected; smoke is structural validation only, full sweep uses 5 codebooks at N=1024). Self-test passes 9/9 cases.
- Anchor 2: N=64 1-seed 3-alpha -> KILLED via small-N artifact (BBMD distances ~5 because un-normalized +/-1 entries dominate sqrt(64) scaling; max VAMP-rel-err 0.40 at sub-capacity). Smoke validates structure; full N=1024 sweep is the discriminating run. Self-test passes 8/8 cases.

Both scripts produced valid metrics.json with positive structural assertions. Remote-side gate `--self-test` passed (2.6s and 2.8s respectively).

## Pipeline implications

- Total CPU span: ~45-90 min behind existing GPU+remote queue (3rd in remote line: kerdock_2design_v3_stim runs first, then MP-KS pre-test, then interp-family cross-check).
- GPU queue (overnight_queue): 5 pending (untouched).
- Remote CPU queue: 3 pending (kerdock_2design_v3_stim, this anchor 1, this anchor 2).
- Local CPU queue: 0 pending (all 9 terminal: 7 completed, 2 killed).
- Queue-depth invariant per [[feedback-pipeline-pacing]] satisfied: depth >= 1 on remote CPU for ~90 min ahead.

## Honest framing per [[feedback-no-smoke]]

These are NARROW infrastructure-class rehab anchors, NOT substrate-physics novelty. Per Research's deep assessment: even with both PASSing, the resulting "12th capability" will be infrastructure-class (R3) or meta-tool (R1) — narrower than the original BBMD-as-substrate-novel-class ambition. Per the rehab assessment: if both pass, the 12th capability emerges as a composite "pre-flight + diagnostic" infrastructure capability; if both fail, consolidate at 11 with v171 annotation-clarifications on Cap 1/3/8 + v164a + v163.

## PROT compliance

- Pause flag CLEARED, confirmed by orchestrator pre-dispatch.
- Both scripts include `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top.
- Both preregs include formula self-test cells per [[feedback-strategy-spec-formula-selftests]] (9 cells for Anchor 1; 8 cells for Anchor 2).
- Background execution per [[feedback-no-blocking-runs]]: queue is non-blocking.
- 2 status_log entries to be written (HIGH x2: first test of two infrastructure-class capability candidates).
