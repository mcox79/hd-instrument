# exp_dev cycle 6 queue note -- 7 anchors shipped

queue=remote_cpu_queue name=q_f5_oscillating_envelope_v1 script=experiments/exp_q_f5_oscillating_envelope_v1.py prereg=preregs/2026-06-02_q_f5_oscillating_envelope_v1.md timeout=600
queue=remote_cpu_queue name=q_f6_pq_distribution_v1 script=experiments/exp_q_f6_pq_distribution_v1.py prereg=preregs/2026-06-02_q_f6_pq_distribution_v1.md timeout=1800
queue=remote_cpu_queue name=f4_free_cumulants_v1 script=experiments/exp_f4_free_cumulants_v1.py prereg=preregs/2026-06-02_f4_free_cumulants_v1.md timeout=120
queue=remote_cpu_queue name=caching_lru_lfu_hybrid_v1 script=experiments/exp_caching_lru_lfu_hybrid_v1.py prereg=preregs/2026-06-02_caching_lru_lfu_hybrid_v1.md timeout=120
queue=remote_cpu_queue name=caching_admission_control_v1 script=experiments/exp_caching_admission_control_v1.py prereg=preregs/2026-06-02_caching_admission_control_v1.md timeout=300
queue=remote_cpu_queue name=caching_eviction_cost_amortized_v1 script=experiments/exp_caching_eviction_cost_amortized_v1.py prereg=preregs/2026-06-02_caching_eviction_cost_amortized_v1.md timeout=120
queue=remote_cpu_queue name=hippocampal_place_field_v1 script=experiments/exp_hippocampal_place_field_v1.py prereg=preregs/2026-06-02_hippocampal_place_field_v1.md timeout=120

## Dropped (blocked)
- substrate_spectral_health_check_v1: INSTRUMENTATION_SUSPECT -- Z-score formula mismatched to diagonal-removed Hopfield W
- tau_mem_m_sweep_v1: T_MAX << tau_theory, redesign with decay-rate fit or larger gamma
- multiagent_emergence_v1: smoke HARD_FAIL (LAMBDA_SHARED=0.5 too weak, redesign v2 with 0.8)

## Instantly completed (fast N=1024 CPU)
- f4_free_cumulants_v1: HARD_FAIL N=1024 (M4 mismatch confirms formula error; diagonal removal not in theory)
- caching_lru_lfu_hybrid_v1: MIDDLE_BAND (rho=0.732, recency-only; frequency not encoded in eigenvalue score)

Acted-on 2026-06-02: cycle 6 ship absorbed into v331 + v332 cap_map updates
