# Prereg: wave14_cap12_cap6_conformal_routing_subsumption_v1

**Date**: 2026-05-24
**Vertex**: CONFORMAL_ROUTING_SUBSUMPTION_PASS / KILLED / INCONCLUSIVE
**Capability target**: Composition B (Cap 12 ✅ x Cap 6 ✅) — proactive cross-capability drill from Strategy
**Queue**: `remote_cpu_queue` (~30 min CPU)
**Script**: `experiments/exp_wave14_cap12_cap6_conformal_routing_subsumption_v1.py`

## Background

Cap 12 (AMP-vs-VAMP routing infrastructure) ships an MP-KS pre-test that produces a single scalar routing decision: ks <= tau -> AMP_OK, else VAMP_REQUIRED. Cap 6 (Venn-Abers conformal calibration) ships a finite-sample distribution-free calibration wrapper. This experiment tests Composition B: does wrapping Cap 12's routing in Cap 6's calibration produce a useful commit-vs-abstain primitive?

The κ_n-divergence score (= MP-KS score in this construction) is a natural non-conformity score; Cap 6 wraps Cap 12's routing decisions in calibrated coverage. Same conformal family that rescued Cap 2 at v172.

## Hypothesis

Venn-Abers conformal calibration on the MP-KS score produces commit-vs-abstain decisions that are correct on every codebook that gets at least one commit, with overall abstain-rate below 30%. The calibration adds value (avoids confidently-wrong routings) without becoming useless conservatism.

## Design

- N=1024, M/N=1.0, 5 codebooks × 5 seeds = 25 observations (matches v175 Cap 12 baseline).
- Compute MP-KS score and AMP rel-err for each of the 25 obs (empirical_label = AMP_OK if amp_rel < 0.10).
- Apply LOO Venn-Abers conformal calibration: for each held-out (cb, seed), use the remaining 24 obs as the calibration set; compute p_AMP and p_VAMP via the Vovk-Petej formula on label-restricted non-conformity scores.
- COMMIT iff p[routed_label] >= 0.90 AND p[other_label] < 0.50; otherwise ABSTAIN.
- Aggregate: per-codebook commit accuracy (does every committed routing match the empirical label?); total abstain_rate.

## HARD PASS (Composition B licensed)

- **per_codebook_commit_accuracy = 5/5** (every codebook that got at least one commit has all its committed routings correct)
- **AND abstain_rate < 0.30** (calibration stays useful, doesn't refuse most decisions)

## HARD FAIL

- **per_codebook_commit_accuracy < 4/5** (calibration doesn't actually improve over raw routing)
- **OR abstain_rate >= 0.70** (refusing too much; calibration is useless conservatism)

## MIDDLE BAND

- **per_codebook_commit_accuracy = 4/5 AND abstain_rate < 0.70** — improvement but not full; Composition B stays at 🟡.

## Formula self-tests (10/10 pass)

1. `route_from_ks` boundary cases (KS ≤ tau → AMP_OK)
2. `empirical_truth_from_amp_rel` boundary cases (amp_rel < 0.10 → AMP_OK)
3. Venn-Abers p-value formula on lower-KS new obs, AMP_OK calibration → p=1.0
4. Venn-Abers p-value formula on higher-KS new obs, AMP_OK calibration → p=0.2
5. Venn-Abers p-value formula for VAMP candidate (sign flip on non-conformity)
6. `commit_decision` logic (p_routed >= 0.90 AND p_other < 0.50 → COMMIT)
7. Compute_verdict PASS on synthetic 5/5 codebook all-correct data
8. Compute_verdict HARD FAIL via excessive abstain (25/25 abstain)
9. Compute_verdict MIDDLE BAND on 4/5 all-correct
10. Compute_verdict INCONCLUSIVE on missing folds

## Acceptance for queue submission

- [x] Script includes `sys.stdout.reconfigure` block
- [x] Script includes atomic metrics-write block
- [x] Script includes env-var-driven `HDLAB_EXP_NAME` outdir
- [x] Self-test runs at start of `run_main`
- [x] Pre-run smoke at N=64 / 1 seed / 2 codebooks completed locally; produced valid metrics.json (INCONCLUSIVE via "too few folds" branch — expected for smoke scale)
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg. Orchestrator invocation explicitly stated "Pause flag CLEARED."

## Honest framing

Composition B is a META-tool capability: it gates whether Cap 12 routing decisions ship to customers with conformal coverage guarantees, or whether the wrapper produces useless conservatism. PASS adds a customer-visible quality signal ("the substrate doesn't just say AMP_OK; it commits to AMP_OK with calibrated 90% confidence"). FAIL doesn't damage Cap 12 directly; it just means Cap 6 doesn't wrap Cap 12 productively at the v175 N=1024 scale.
