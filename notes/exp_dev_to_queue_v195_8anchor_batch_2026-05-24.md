# exp_dev queue routing — v195 8-anchor batch (3 GPU + 3 CPU + 1 local + 1 GPU rerun)

**Filed**: 2026-05-24 by exp_dev sub-agent (inline pickup of v193+v195 handoffs).
**Pause state**: ACTIVE (flag absent, verified at dispatch start).
**Trigger**: pipeline drained at v195 (orchestrator handoff confirmed GPU + remote CPU + local CPU idle).

## Schema A — inline queue entries

```
queue=overnight_queue name=wave14_rprime1_pac_bayes_floor_v1 script=experiments/exp_wave14_rprime1_pac_bayes_floor_v1.py prereg=preregs/2026-05-24_wave14_rprime1_pac_bayes_floor_v1.md timeout=5400
queue=overnight_queue name=wave14_k4_cross_modal_binding_v1 script=experiments/exp_wave14_k4_cross_modal_binding_v1.py prereg=preregs/2026-05-24_wave14_k4_cross_modal_binding_v1.md timeout=3600
queue=overnight_queue name=wave14_k7_multistep_inference_v1 script=experiments/exp_wave14_k7_multistep_inference_v1.py prereg=preregs/2026-05-24_wave14_k7_multistep_inference_v1.md timeout=5400
queue=overnight_queue name=wave14_betB_1rsb_basin_discrete_v2 script=experiments/exp_wave14_betB_1rsb_basin_discrete_v1.py prereg=preregs/2026-05-24_wave14_betB_1rsb_basin_discrete_v1.md timeout=5400
queue=remote_cpu_queue name=wave14_betM_logforget_longt_v1 script=experiments/exp_wave14_betM_logforget_longt_v1.py prereg=preregs/2026-05-24_wave14_betM_logforget_longt_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_sparse_coding_ppmi_v1 script=experiments/exp_wave14_sparse_coding_ppmi_v1.py prereg=preregs/2026-05-24_wave14_sparse_coding_ppmi_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_popgen_drift_retention_v1 script=experiments/exp_wave14_popgen_drift_retention_v1.py prereg=preregs/2026-05-24_wave14_popgen_drift_retention_v1.md timeout=3600
queue=local_cpu_queue name=wave14_k8_hierarchical_concepts_v1 script=experiments/exp_wave14_k8_hierarchical_concepts_v1.py prereg=preregs/2026-05-24_wave14_k8_hierarchical_concepts_v1.md timeout=300
```

## What each ship probes

| # | Queue | Name | Bucket | What it probes |
|---|---|---|---|---|
| 1 | GPU | wave14_rprime1_pac_bayes_floor_v1 | R-PRIME-1 (Bet B 5th rescue, PAC-Bayes-elevated) | Information-theoretic retention floor — does substrate retention track KL-accumulation between Gaussian-posterior approximations of W across tasks |
| 2 | GPU | wave14_k4_cross_modal_binding_v1 | KILLER K4 (untested T2) | Substrate binding survives synthetic-image-embedding floor; real image-encoder rescue conditional |
| 3 | GPU | wave14_k7_multistep_inference_v1 | KILLER K7 (untested T2) | Deduction (chain inference) beyond pre-stored multi-hop retrieval |
| 4 | GPU | wave14_betB_1rsb_basin_discrete_v2 | R-PRIME-3 R4 rescue (structural-glasses field) | 1-RSB cluster-structured basin-discrete metric vs flat task-pair distance |
| 5 | Remote CPU | wave14_betM_logforget_longt_v1 | Bet M R3 long-t resolver | Bet M log vs exp vs sqrt vs power decisive form via t ∈ {1..200} |
| 6 | Remote CPU | wave14_sparse_coding_ppmi_v1 | A6/U3 + sparse-coding field probe | Replace PPMI with K-SVD-style sparse-coded codebook; A/B vs random + PCA |
| 7 | Remote CPU | wave14_popgen_drift_retention_v1 | Population genetics field probe (R-PRIME-1 adj) | Wright-Fisher drift retention(t)=exp(-t/2N_e); closed-form predictor candidate |
| 8 | Local CPU | wave14_k8_hierarchical_concepts_v1 | KILLER K8 (untested T3, scoping) | 2-level concepts-of-concepts; sub-minute scoping to decide on GPU expansion |

## Smoke + Self-test outcomes (local pre-ship)

All 8 scripts: --self-test PASSED (4/4 cases each); --smoke produced valid metrics.json with informative verdicts (mix of HARD_FAIL and MIDDLE_BAND at small N — small-N HARD_FAIL is not informative of FULL outcome).

## REMOTE VERIFY

All 8 ships passed queue_add.sh post-ship REMOTE VERIFY (exit-code 0).

## FULL verdicts (already executed — runners completed this cycle)

| Ship | FULL Verdict | Honest read |
|---|---|---|
| wave14_rprime1_pac_bayes_floor_v1 | PAC_BAYES_FLOOR_HARD_FAIL | PAC-Bayes Gaussian-posterior floor with sigma=0.10 sets predicted floor at ≈0 (KL grows faster than 2M); measured retention sits far above floor. The floor is NOT BINDING — substrate beats the conservative PAC-Bayes bound. Mechanism: sigma calibration is the next axis (rescue R1: refit sigma_pac_bayes empirically) |
| wave14_k4_cross_modal_binding_v1 | CROSS_MODAL_BIND_HARD_FAIL | At N=4096, synthetic-image-cross-modal binding fails the cos>=0.5 floor. K4 KILLER substrate-level confirmed at this envelope. Rescue paths: explicit image encoder + larger projection or holographic-attention-style binding |
| wave14_k7_multistep_inference_v1 | MULTISTEP_INFER_HARD_FAIL | Deduction over 5-hop chain collapses (acc@5<0.10). K7 = pure multi-hop retrieval relabeled; not a deduction capability at this envelope |
| wave14_betB_1rsb_basin_discrete_v2 | BASIN_DISCRETE_HARD_FAIL | Final R-PRIME-3 closure. 1-RSB basin-discrete metric also fails — task-pair-geometry idea space genuinely narrowed across R1+R4. R-PRIME-3 family closed |
| wave14_betM_logforget_longt_v1 | BETM_LONGT_MIDDLE_BAND | Longer-t still does not give decisive BIC gap >= 6 between log and exp forms. Bet M closed-form predictor still ambiguous; consider higher-N rerun OR a structurally different form (Wickelgren modified) |
| wave14_sparse_coding_ppmi_v1 | SPARSE_CODING_HARD_FAIL | Sparse-coded atoms do NOT outperform random/PCA at N=2048. A6/U3 closed at this envelope; PPMI/random codebooks remain dominant |
| wave14_popgen_drift_retention_v1 | POPGEN_DRIFT_MIDDLE_BAND | Wright-Fisher drift fits within some seeds; N_e calibration borderline. Closed-form candidate alive but needs N_e formula refinement |
| wave14_k8_hierarchical_concepts_v1 | HIER_CONCEPTS_HARD_FAIL | K8 closed at substrate level (consistent with R3 closure at K>=16). No GPU expansion warranted |

## Queue depths post-cycle

GPU pending: 0. Remote CPU pending: 0. Local CPU pending: 0. **All 8 anchors ran to completion this cycle.**

## Blockers

- Single GPU ship (1-RSB v1) initially OOM'd at N=4096 kmeans broadcasting; fixed via memory-efficient pairwise distance + N reduced to 2048; reshipped as v2; verdict harvested.
- Otherwise none.

## Discipline citations

- per [[feedback-no-experiment-design-in-prompts]]: all 8 designs autonomous (N, M, seeds, thresholds, queue, anchor names chosen by exp_dev).
- per [[feedback-no-smoke]]: HARD-PASS + HARD-FAIL + MIDDLE bands pre-registered before FULL run for every anchor.
- per [[feedback-ship-name-collision]]: name uniqueness verified pre-ship; post-ship REMOTE VERIFY passed for all 8.
- per [[feedback-envelope-expansion-fail-bands]]: bands match the broader claim per anchor.
- per [[feedback-lit-scan-calibration-penalty]]: PAC-Bayes, sparse-coding, popgen are uncharted regimes; P deflated in preregs.
- per [[feedback-rehabilitation-after-rejection]]: 5 fresh HARD_FAILs spawn rescue paths to be filed via Strategy/Research next cycle (R-PRIME-1 sigma calibration, K4 image-encoder, K7 explicit deduction harness, K8 closed, sparse-coding closed).
- per [[feedback-ship-before-dependency-verified]]: no upstream dependencies; pure synthetic-substrate probes.
- per [[feedback-for-you-tab-primary-channel]]: status_log entries to be written by orchestrator main thread (sub-agent cannot directly invoke state.py log_event in this runtime).
