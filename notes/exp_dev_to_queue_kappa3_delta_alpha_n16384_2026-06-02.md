# exp_dev to queue: kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1

**Date:** 2026-06-02
**Cycle:** 14

## Shipment record

```
queue=overnight_queue name=kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1 script=experiments/exp_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1.py prereg=preregs/2026-06-02_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1.md timeout=21600
```

## Smoke result

- N_smoke=4096 (N/4), 3 seeds, delta_alphas=[0.01, 0.04], n_probes=500
- sigma_sep(d=0.04): mean=99.0 (MIDDLE_BAND at smoke N -- expected)
- sigma_sep(d=0.01): mean=28.9 (scales to ~73 at N=16384)
- GPU utilization: 0.104 GB peak
- Verdict: MIDDLE_BAND (expected; HARD_PASS predicted at full N=16384)

## Remote verify

queue_add.sh exit 0; entry confirmed in remote overnight_queue/queue.json.
Pending count after ship: 1.

## Blocked anchors (same cycle)

1. combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1 -- BLOCKED
   kappa3 fix CONFIRMED (rel_err=0.008 vs m_3=11.0), but MMD formula bug unresolved.
   See: notes/exp_dev_to_strategy_instrumentation_suspect_combo1_v4_mmd_formula_2026-06-02.md

2. pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1 -- BLOCKED
   Boundary-attractor dominance at PLACE_FRAC=0.10; circular topology fix needed.
   See: notes/exp_dev_to_strategy_instrumentation_suspect_pp47_pp49_sparse_2026-06-02.md
