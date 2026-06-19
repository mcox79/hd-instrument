# exp_dev queue shipment: R2 + R4 K-transition anchors 2026-06-01

Shipped 2 anchors from strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md.

```
queue=remote_cpu_queue name=path_d_k_fine_grained_transition_v1_n4096 script=experiments/exp_path_d_k_fine_grained_transition_v1_n4096.py prereg=preregs/2026-06-01_path_d_k_fine_grained_transition_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=path_d_k1_cross_n_null_prediction_v1_n4096 script=experiments/exp_path_d_k1_cross_n_null_prediction_v1_n4096.py prereg=preregs/2026-06-01_path_d_k1_cross_n_null_prediction_v1_n4096.md timeout=14400
```

## Anchor A: path_d_k_fine_grained_transition_v1_n4096

R2 from v307 follow-on. Fine-grained K transition curve at fixed M=16N=65536.
K_paths sweep {1,2,3,5,10,100}; 5 seeds; N=4096.
HP: monotone increase; K=2 in [0.10,0.30]; K=3 in [0.40,0.70]; K=5 in [0.85,0.99].
HF: K=2/3/5 all at random-chance (<= 0.01).
MIDDLE: discontinuous cliff at specific K.
Smoke: PASS. Remote verify: PASS.

## Anchor B: path_d_k1_cross_n_null_prediction_v1_n4096

R4 from v307 follow-on. K=1 cross-N null-prediction test for P3 percolation framework.
N sweep {4096, 16384} (N=8192 skipped: Kerdock log2(8192)=13 odd constraint).
K=1 fixed, depth=5, M=16N. 5 seeds.
HP: max|acc_N - 0.022| <= 0.01 (N-independence HOLDS).
HF: max|acc_N - 0.022| > 0.03 (N-driven, percolation framing weakens).
MIDDLE: delta in (0.01, 0.03].
Smoke: PASS. Remote verify: PASS.

## GHRR deferred

GHRR (R3 from routing) deferred 1-2 weeks per sequencing recommendation
in the routing file. Sequence after Week 1 GO/NO-GO per testbed bandwidth.


---

Acted-on 2026-06-01: anchor shipped + K_fine_transition MIDDLE_BAND-LABEL-UNDER-CLAIM verdict #169 processed in v308


Acted-on 2026-06-01: anchor shipped + K_fine_transition MIDDLE_BAND-LABEL-UNDER-CLAIM verdict #169 processed in v308
