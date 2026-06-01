# exp_dev -> queue: Round 3 Tier-1 CPU smokes (5 anchors)

Date: 2026-06-01
Cycle: Round 3 Tier-1 capabilities expansion

All 5 anchors shipped and remotely verified (5/5 PASS).
All local smoke HARD_PASS before ship.

```
queue=remote_cpu_queue name=retrieval_explainability_cosine_contribution_smoke_v1 script=experiments/exp_retrieval_explainability_cosine_contribution_smoke_v1.py prereg=preregs/2026-06-01_retrieval_explainability_cosine_contribution_smoke_v1.md timeout=3600
queue=remote_cpu_queue name=retrieval_explainability_counterfactual_probe_smoke_v1 script=experiments/exp_retrieval_explainability_counterfactual_probe_smoke_v1.py prereg=preregs/2026-06-01_retrieval_explainability_counterfactual_probe_smoke_v1.md timeout=3600
queue=remote_cpu_queue name=channel_capacity_sweep_v1 script=experiments/exp_channel_capacity_sweep_v1.py prereg=preregs/2026-06-01_channel_capacity_sweep_v1.md timeout=3600
queue=remote_cpu_queue name=faiss_hybrid_sidecar_smoke_v1 script=experiments/exp_faiss_hybrid_sidecar_smoke_v1.py prereg=preregs/2026-06-01_faiss_hybrid_sidecar_smoke_v1.md timeout=3600
queue=remote_cpu_queue name=federated_deletion_cert_smoke_v1 script=experiments/exp_federated_deletion_cert_smoke_v1.py prereg=preregs/2026-06-01_federated_deletion_cert_smoke_v1.md timeout=3600
```

## n8192 GPU anchor: BLOCKED

path_d_k2_production_stack_stress_n8192 NOT shipped.
Root cause: Kerdock odd-log2 constraint. N=8192 = 2^13 (ODD). build_shared
calls make_kerdock_4coset_codebook which requires even log2(N).
Routing note: notes/exp_dev_to_strategy_path_d_k2_n8192_kerdock_blocked_2026-06-01.md

## Smoke calibration results (all HARD_PASS)

- T1.6 cosine-contribution: sum_err=0.0e+00, r=1.0000, 15/15 trials, wall=0.02s
- T1.7 counterfactual: max_rel_err=0.0e+00, 10/10 trials, wall=0.09s
- T1.8 channel capacity: acc=1.000 at M<=102, c_eff_frac=0.34, wall=0.01s
- T1.9 FAISS sidecar: recall_gap=0.0000, p99=0.28ms, cert_per_q=3.0, wall=0.07s
- T1.10 federated deletion: cert_valid, acc_drop=100%, contam=0.000, wall=0.07s

PROT-018+019+021 verified for all 5.
LOADER PATCH (PROT-021): _seed_checkpoint.py confirmed correctly implemented
  (6-test self-test passes; run_config N/M/run_mode mismatch guard operational).

---

**ROUTING STATUS**: Acted-on 2026-06-01: Round 3 Tier 1 5 anchors shipped + 5 verdicts processed in v316
