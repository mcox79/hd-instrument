## exp_dev Cycle 20 queue refill (2026-06-03)

### Context
Triggered by: Cycle 20 batch complete (7 verdicts), both queues empty, pause flag ABSENT.
cap_map v351 open handoffs: Q-A3 L=19 GPU ceiling, PP-56 N=8192 CPU band-lift, PP-33 R4 N-scale, PP-49 CF R2 redesign, Q-B1 d-120/N=32768, PP-50 capacity R3 N-sweep.

### Anchors shipped

1. **q_a3_l19_cross_layer_composition_v1_n4096** -> overnight_queue, timeout=14400s
   - Rationale: Q-A3 L=17 and L=18 both EXACT-1.0 unanimous 5-seed. Ceiling not found. Direct continuation.
   - Smoke: CUDA unavailable locally; structure verified (import chain, PROT-018 N binding, self-test). L=17/L=18 elapsed < 2s each; PROT-019 floor 14400s applies.
   - Pre-reg: preregs/2026-06-02_q_a3_l19_cross_layer_composition_v1_n4096.md
   - PROT-018 OK (gate verified N=4096). PROT-019 OK (14400s >= floor). PROT-022 OK (self-test passed 2.0s).

2. **sherman_morrison_rank1_deletion_cert_drop_v1_n8192** -> remote_cpu_queue, timeout=21600s
   - Rationale: PP-56 NEW ROW (v351). Single N=4096 founding point; BAND-LIFT eligibility requires 2-N cross-N (N=4096 + N=8192). Theory cert_ratio(N=8192)=0.000122 (half of N=4096=0.000244).
   - Smoke: N=1024, cert_ratio=0.000966 << HP=0.15 (HARD_PASS direction). retained_delta=0.003854 << HP=0.10. N-monotone expected at full N=8192.
   - Pre-reg: preregs/2026-06-02_sherman_morrison_rank1_deletion_cert_drop_v1_n8192.md
   - PROT-018 OK (N=8192). PROT-019 OK (21600s >= floor 21600s; raw estimate 48s too short, floor applied). PROT-022 OK (self-test passed 2.6s).

3. **activation_barrier_n_scale_v1_n8192** -> remote_cpu_queue, timeout=21600s
   - Rationale: PP-33 LVH #209: v2_n4096 mean ratio=1.0962 below MIDDLE lower bound; honest tag BELOW_MIDDLE. R4 N-scale test: does ratio increase at N=8192? HP gate = ratio>1.20 AND n_monotone>=4/5.
   - Smoke: N=1024, ratio=1.15 (MIDDLE, +5% improvement over N=4096). Direction positive.
   - Pre-reg: preregs/2026-06-03_activation_barrier_n_scale_v1_n8192.md
   - PROT-018 note: no _nN suffix in anchor (alpha-sweep; gate matched _n8192 in name anyway); PROT-019 floor 21600s applied (raw 57s). PROT-022 OK (self-test passed 2.4s).

### Deferred (upstream routing)

- **PP-49 CF R2 redesign**: substitution d1-d5 all HARD_FAIL at N=4096. d4 partial isolated (mean=0.189, high per-seed variance, not robust). R2 requires redesign spec before implementation. Routing to strategy for axis-combination redesign spec before next exp_dev cycle.
- **Q-B1 d-120 or N=32768**: v351 BAND-LIFT just triggered; queue has PP-56 + PP-33 as higher-priority CPU items. d-120 extension deferred one cycle.
- **PP-50 capacity R3 N-sweep**: envelope refined in v351; deferred one cycle (3 CPU experiments already justified; no padding per [[feedback-no-padding-experiments]]).

### Totals
overnight_queue pending: +1 (GPU)
remote_cpu_queue pending: +2 (CPU)
Deferred to strategy: PP-49 CF R2, Q-B1 d-120, PP-50 R3 N-sweep
