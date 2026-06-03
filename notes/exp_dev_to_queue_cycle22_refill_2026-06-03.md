# exp_dev queue routing note -- CYCLE 22 refill 2026-06-03

3 anchors shipped. All REMOTE VERIFIED.

```
queue=overnight_queue name=q_a3_l22_cross_layer_composition_v1_n4096 script=experiments/exp_q_a3_l22_cross_layer_composition_v1_n4096.py prereg=prereqs/2026-06-03_q_a3_l22_cross_layer_composition_v1_n4096.md timeout=14400
queue=overnight_queue name=q_b1_chain_depth_200_v1_n16384 script=experiments/exp_q_b1_chain_depth_200_v1_n16384.py prereg=prereqs/2026-06-03_q_b1_chain_depth_200_v1_n16384.md timeout=21600
queue=remote_cpu_queue name=pp58_isochoric_kappa3_multialpha_v1_n4096 script=experiments/exp_pp58_isochoric_kappa3_multialpha_v1_n4096.py prereg=prereqs/2026-06-03_pp58_isochoric_kappa3_multialpha_v1_n4096.md timeout=14400
```

Justifications:
- q_a3_l22: Q-A3/PP-12 L-ceiling chase (8th extension, L=15..L=21 all EXACT-1.0000; L=22 next)
- q_b1_d200: Q-B1/PP-49a depth ceiling probe (3x N=16384 flat-profile; extend d150->d200)
- pp58_multialpha: PP-58 R3 rescue: audit_crit recalibration across alpha={0.10,0.20}
