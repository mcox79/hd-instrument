# exp_dev -> queue: v193 queue refill batch (6 ships)

**Filed**: 2026-05-24 exp_dev (autonomy refill per hand-off `notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md`)
**Pause state**: ABSENT (verified `data/orchestrator_paused.flag` does not exist)

## Routing entries (Schema A inline key=value)

```
queue=overnight_queue name=wave14_rprime2_moe_K_sweep_v1 script=experiments/exp_wave14_rprime2_moe_K_sweep_v1.py prereg=preregs/2026-05-24_wave14_rprime2_moe_K_sweep_v1.md timeout=5400
queue=overnight_queue name=wave14_K6_compositional_holdout_v1 script=experiments/exp_wave14_K6_compositional_holdout_v1.py prereg=preregs/2026-05-24_wave14_K6_compositional_holdout_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_fieldA_lyapunov_spectrum_v1 script=experiments/exp_wave14_fieldA_lyapunov_spectrum_v1.py prereg=preregs/2026-05-24_wave14_fieldA_lyapunov_spectrum_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_F6_boolean_kkl_v1 script=experiments/exp_wave14_F6_boolean_kkl_v1.py prereg=preregs/2026-05-24_wave14_F6_boolean_kkl_v1.md timeout=2400
queue=remote_cpu_queue name=wave14_rprime3_R1_alt_geometry_v1 script=experiments/exp_wave14_rprime3_R1_alt_geometry_v1.py prereg=preregs/2026-05-24_wave14_rprime3_R1_alt_geometry_v1.md timeout=2400
queue=local_cpu_queue name=wave14_betM_logforget_fitform_v1 script=experiments/exp_wave14_betM_logforget_fitform_v1.py prereg=preregs/2026-05-24_wave14_betM_logforget_fitform_v1.md timeout=600
```

## Anchor table

| # | Queue | Name | Anchor | Smoke verdict | FULL verdict (post-run) |
|---|---|---|---|---|---|
| 1 | overnight | wave14_rprime2_moe_K_sweep_v1 | R-PRIME-2 MoE M_c falsifier (TOP priority post-R-PRIME-3 closure v193) | MOE_KSWEEP_HARD_FAIL_REJECTED (smoke-scale, M too low) | MOE_KSWEEP_HARD_FAIL_REJECTED |
| 2 | overnight | wave14_K6_compositional_holdout_v1 | K6 compositional generalization axis 2 (hierarchical pre-binding) | K6_HARD_FAIL_NO_GENERALIZATION (smoke) | K6_HARD_FAIL_NO_GENERALIZATION |
| 3 | remote_cpu | wave14_fieldA_lyapunov_spectrum_v1 | Field-A reservoir Lyapunov spectrum (cross-framework cadence) | LYAP_HARD_FAIL_FAR_FROM_EDGE (smoke, small N expected chaotic) | LYAP_HARD_FAIL_FAR_FROM_EDGE |
| 4 | remote_cpu | wave14_F6_boolean_kkl_v1 | F-6 Boolean KKL probe (v183 residual re-ship) | KKL_HARD_PASS_LOW_INFLUENCE | KKL_HARD_PASS_LOW_INFLUENCE |
| 5 | remote_cpu | wave14_rprime3_R1_alt_geometry_v1 | R-PRIME-3 R1 rescue (alt-geometry Wasserstein-1 metric) | RPRIME3_R1_HARD_PASS_ALT_GEOMETRY_RESCUE (smoke; 3 pairs only) | RPRIME3_R1_HARD_FAIL_GEOMETRY_NARROWED |
| 6 | local_cpu | wave14_betM_logforget_fitform_v1 | Bet M log-forgetting fit-form selection HARNESS (post-Allen-Cahn rejection v193) | BETM_LOGFORGET_HARD_FAIL_HARNESS_REJECTED (smoke; 5 reps × 5 t-points only) | BETM_LOGFORGET_MIDDLE_BAND (4/5 correct, median_BIC_gap=2.23) |

## REMOTE VERIFY confirmation

All 5 remote ships verified via queue_add.sh's post-ship `Where-Object name -eq <NAME>` SSH check. Local ship verified by file presence in `data/local_cpu_queue/queue.json`.

## Strong findings (for orchestrator follow-up)

- **R-PRIME-2 (MoE) HARD-FAIL at FULL**: top-priority falsifier closed in single cycle. MoE-on-substrate REJECTED at N=4096, M_total=4096, K in {2,4,8,16}. Trigger Research drill per [[feedback-negative-results-2x-research]].
- **R-PRIME-3 R1 HARD-FAIL at FULL**: alt-geometry rescue FAILS at full scale (smoke false-positive — 3 pairs underpowered). Now both inner-product AND Wasserstein-1 metrics flat. R-PRIME-3 idea space narrowed further; move to R2 sub-corpus geometry rescue.
- **Field-A (reservoir Lyapunov) HARD-FAIL**: substrate is firmly chaotic at all 3 probed densities. Field-A reservoir-computing mapping REJECTED. Save Week-2 budget per hand-off contract.
- **K6 (compositional generalization) HARD-FAIL**: Hadamard-product hierarchical pre-binding does NOT generalize to held-out pairs at FULL N=4096. K6 axis 2 REJECTED; promote axes 3 (cleanup-iteration) and 4 (Bet X position-indexed).
- **F-6 (Boolean KKL) HARD-PASS**: substrate boundaries are low-influence / well-distributed (max_inf_share <= 0.30, KKL ratio >= 1.0 at both densities). Boolean-analysis row 🔬 -> 🟡 promotion candidate.
- **Bet M log-forgetting harness MIDDLE_BAND**: 4/5 forms correctly identified (just shy of 5/5 PASS), median_BIC_gap=2.23 (below 4.0 PASS, above 2.0 FAIL). Harness is borderline-validated; usable for real-data fits but should report top-2 BICs.

## Final queue depths (post-cycle)

- overnight_queue: 5 PRE-EXISTING pending (wave14_betA_continual_edit_5seed_v3, wave14_cap2_confidence_margin_probe_v1, wave14_pq_high_resolution_v1, wave14_demo1_noise_envelope_v1, wave14_R_transform_kerdock_v1_multi_N) + 2 shipped this cycle (BOTH COMPLETED already). Net depth: 5 pending (depth >= 1 maintained).
- remote_cpu_queue: 0 pending (3 shipped this cycle ALL COMPLETED). Net depth: 0 — needs refill next cycle.
- local_cpu_queue: 0 pending (1 shipped + completed). Net depth: 0.

## Blockers

None. Pause flag absent; queue_add.sh verified all 6 ships into target queues; runners executed all 6 within minutes; all 6 produced valid metrics.json with terminal verdicts.

## Follow-up triggers for next cycle

1. **Verdict handler dispatch** for all 6 verdicts (4 HARD-FAIL, 1 HARD-PASS, 1 MIDDLE) -> cap_map update.
2. **Per [[feedback-negative-results-2x-research]]**: 2x Research drill on R-PRIME-2 closure (genuine refutation, not OOM).
3. **Pipeline refill**: GPU depth=5 pending pre-existing, but remote_cpu_queue + local_cpu_queue both at depth 0. Trigger next exp_dev cycle.
