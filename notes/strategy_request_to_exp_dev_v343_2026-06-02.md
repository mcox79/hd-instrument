## exp_dev refill request (v343, 2026-06-02, queue=0 post cycle-13)

Queue is empty post cycle-13. Cap_map state: v343. Pause flag: ABSENT. Pipeline-pacing active.

Priority routing (from v343 state transitions):

1. Q-B1 depth-50+ (ceiling not reached at d45=0.596; depth-50/55 warranted at N=8192)
2. PP-52 N=32768 (4th N-cross-rung; test whether rollback/addition hold at next scale)
3. Q-A3 L=12+ (find fidelity degradation depth beyond L=10; current all 1.0000)
4. Hebbian-LoRA R1 rescue: constrained-Hebbian acc-gate (acc_delta<=0.02 gate BEFORE speedup claim)
5. PP-48 NKT cross-N (depth-11 or depth-13 at N=8192 to enable band-lift via cross-N criterion)

Strategy note: Q-B1 depth-50+, PP-52 N=32768, Q-A3 L=12+, and R1 Hebbian rescue are all GPU. PP-48 cross-N is GPU.

Exp Dev: design next batch from above priorities. Use smoke-then-full pipeline. Pre-register HP/MID/HF bands before queue_add.sh. Cap_map v343 is authoritative state for band thresholds.
