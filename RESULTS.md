# Results log

| Date | Experiment | Outcome | Key metric | Notes |
|---|---|---|---|---|
| 2026-05-16 | diagnostic | PASS | Hebbian ratio=1.0000, agent_sim=0.643 | [pdf](data/diagnostic/dashboard.pdf) [trace](data/diagnostic/trace.duckdb) [metrics](data/diagnostic/metrics.json) |
| 2026-05-16 | diagnostic | PASS | Hebbian ratio=1.0000, agent_sim=0.643, attention_rejections=1/4 | [pdf](data/diagnostic/dashboard.pdf) [trace](data/diagnostic/trace.duckdb) [metrics](data/diagnostic/metrics.json) |
| 2026-05-16 | exp_a1_recovery | PASS | k=50 recovery=100.0%; off-diag sim std=0.0221 (theory=0.0312) | [pdf](data/exp_a1_recovery/dashboard.pdf) [trace](data/exp_a1_recovery/trace.duckdb) [metrics](data/exp_a1_recovery/metrics.json) |
| 2026-05-16 | exp_a2_noisy | PASS | recovery@sigma=0.5 = 100%, @sigma=1.0 = 100%, @sigma=2.0 = 100% | [pdf](data/exp_a2_noisy/dashboard.pdf) [trace](data/exp_a2_noisy/trace.duckdb) [metrics](data/exp_a2_noisy/metrics.json) |
| 2026-05-16 | exp_a3_attention | REVIEW | best F1=1.000 at attention=0.10 (P=1.00, R=1.00); precision rises 0.50 -> 0.00 | [pdf](data/exp_a3_attention/dashboard.pdf) [trace](data/exp_a3_attention/trace.duckdb) [metrics](data/exp_a3_attention/metrics.json) |
| 2026-05-16 | exp_a4_hebbian | PASS | freq-RECOGNIZED mean=9.59 vs rare=2.08 (ratio=4.61); 1000/1000 correct retrievals | [pdf](data/exp_a4_hebbian/dashboard.pdf) [trace](data/exp_a4_hebbian/trace.duckdb) [metrics](data/exp_a4_hebbian/metrics.json) |
| 2026-05-16 | exp_a5_envelope | PASS | k=10 breaks at sigma=3.0, k=2000 breaks at sigma=3.0; N=128 breaks at sigma=3.0, N=4096 breaks at sigma=3.0 | [pdf](data/exp_a5_envelope/dashboard.pdf) [trace](data/exp_a5_envelope/trace.duckdb) [metrics](data/exp_a5_envelope/metrics.json) |
