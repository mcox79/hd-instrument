# exp_dev → queue: Cap 12 ✅ continued envelope drills (3 anchors, remote_cpu_queue)

**Date**: 2026-05-24
**Trigger**: Orchestrator silent_idle refill — CPU queue just emptied (E1 finished), Strategy + Research recommend 3 CPU-class probes.
**Pause flag**: ABSENT at dispatch time (orchestrator invocation explicitly said "Pause flag CLEARED"; verified by direct check).

## Three anchors shipped

| queue            | name                                                       | script                                                                     | prereg                                                                  | timeout(s) |
|------------------|------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap12_cap6_conformal_routing_subsumption_v1         | experiments/exp_wave14_cap12_cap6_conformal_routing_subsumption_v1.py      | preregs/2026-05-24_wave14_cap12_cap6_conformal_routing_subsumption_v1.md | 3600       |
| remote_cpu_queue | wave14_kappa_gold_full_e3_v1                               | experiments/exp_wave14_kappa_gold_full_e3_v1.py                            | preregs/2026-05-24_wave14_kappa_gold_full_e3_v1.md                      | 5400       |
| remote_cpu_queue | wave14_mmd_vs_mpks_pretest_v1                              | experiments/exp_wave14_mmd_vs_mpks_pretest_v1.py                           | preregs/2026-05-24_wave14_mmd_vs_mpks_pretest_v1.md                     | 9000       |

## Per-anchor description

**Anchor 1 — Conformal Routing Subsumption (Composition B = Cap 12 ✅ × Cap 6 ✅)**
Tests whether Venn-Abers conformal calibration wrapped on Cap 12's MP-KS routing produces a useful commit-vs-abstain primitive. LOO across 5 codebooks × 5 seeds = 25 obs at N=1024. HARD PASS = 5/5 codebooks all-correct on commits AND abstain_rate < 0.30. HARD FAIL = < 4/5 all-correct OR abstain_rate >= 0.70.

**Anchor 2 — Gold full E3 (Cap 12 ✅ 5th-family stress gate)**
Tests whether the Cap 12 predictor (Spearman ρ of AMP rel-err vs sum-|Δκ_n|) generalizes to a 5th algebraic family — Gold sequences (m=10, N_eff=1023 padded to N=1024) — independent of the Sylvester (SRHT/Hadamard) and 4-coset RM (Kerdock) families. 5 α cells × 10 seeds. HARD PASS = ρ ≥ 0.50 AND max VAMP < 0.15 (relaxed 5th-family thresholds). HARD FAIL = ρ < 0.30 OR max VAMP > 0.30. Quickprobe at α=1 returned BBMD_CANDIDATE (κ_n nontrivial → predictor has signal).

**Anchor 3 — MMD vs MP-KS pre-test audit (Cap 12 ✅ alternative-score audit)**
Tests whether MMD-RBF or Sliced-Wasserstein 1D strictly out-performs MP-KS as the Cap 12 routing non-conformity score. 5 codebooks × 5 seeds at N=1024. Computes 3 scores per codebook (KS, MMD, W1), regresses each against AMP rel-err. HARD PASS = ρ_MMD ≥ 0.75 OR ρ_W1 ≥ 0.75 (5% strict beat over MP-KS v175's 0.70) AND winning score's routing acc ≥ 0.80. HARD FAIL = both ≤ 0.70 AND routing accs ≤ MP-KS's.

## Smoke results

| anchor                                              | smoke verdict                                  | structural validity |
|-----------------------------------------------------|------------------------------------------------|---------------------|
| wave14_cap12_cap6_conformal_routing_subsumption_v1  | INCONCLUSIVE via "too few folds" branch        | OK (2 of 25 folds at smoke N=64, 2 codebooks) |
| wave14_kappa_gold_full_e3_v1                        | KILLED via small-N VAMP blowup (m=6, N=64)     | OK (matches v174/v175 small-N smoke pattern)  |
| wave14_mmd_vs_mpks_pretest_v1                       | INCONCLUSIVE via "missing codebooks" branch    | OK (MP ref mean=1.0037 verified)              |

All 3 self-tests pass: 10/10 (Anchor 1), 9/9 (Anchor 2), 12/12 (Anchor 3). Remote --self-test gates pass: 3.2s + 4.4s + 3.5s.

## SCP dependency note

Anchor 2 depends on `experiments/exp_wave14_kappa_gold_quickprobe_v1.py` (re-imports `gold_sequence_family`). The dep was not present on the remote at first queue-add; SCP'd over directly before successful queue-add. No changes to `queue_add.sh` needed; this is a one-time dependency-SCP that should be added to a future "ship-with-deps" enhancement.

## Queue depth post-ship

- remote_cpu_queue: 3 entries shipped this turn (Anchor 1 has started; Anchors 2 + 3 pending). At the time of the last `queue_add.sh` "queue pending now (2)" report, that's 2 PENDING plus 1 RUNNING (Anchor 1) = 3 active.
- overnight_queue (GPU): unchanged (1 pending E2 N16384 from prior cycle).
- local_cpu_queue: 0 pending.

Queue-depth invariant per [[feedback-pipeline-pacing]] satisfied: ≥ 1 on remote CPU for ~3+ hours ahead (30 min Anchor 1 + 30-45 min Anchor 2 + 2h Anchor 3).

## Blockers

None. Gold m=10 padding (1023 → 1024 via one zero column) verified locally in self-test and smoke. MMD implementation passed identity + shift sanity checks. MP reference sampler swapped from broken inverse-CDF (1/x singularity at lower edge) to empirical eigenvalues of an iid Gauss matrix; verified mean ≈ 1.0 + support ≈ [0, 4] at c=1.
