# exp_dev queue routing note -- Cycle 50 refill (2026-06-04)

Cap_map v381. 15 anchors: 13 GPU (overnight_queue) + 2 CPU (remote_cpu_queue).
Justified by: Q-A3 frontier continuation (108-rung N=16384 + 68-rung N=8192); PP-58 R5 rescue; spectral_monitor v3 rescue.

## Batch A: Q-A3 N=16384 L=128..132 (GPU)
Prereg: prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md
Skip-smoke: 108 prior HARD_PASSes; anchor L=127 elapsed_s=41.7s. Timeout formula: 300s (PROT-019 floor).

queue=overnight_queue name=q_a3_l128_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l128_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md timeout=300
queue=overnight_queue name=q_a3_l129_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l129_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md timeout=300
queue=overnight_queue name=q_a3_l130_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l130_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md timeout=300
queue=overnight_queue name=q_a3_l131_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l131_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md timeout=300
queue=overnight_queue name=q_a3_l132_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l132_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle50_q_a3_n16384_l128_l132.md timeout=300

## Batch B: Q-A3 N=8192 L=89..96 (GPU)
Prereg: prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md
Skip-smoke: 68 prior HARD_PASSes; anchor L=88 elapsed_s=7.53s. Timeout formula: 300s (PROT-019 floor).

queue=overnight_queue name=q_a3_l89_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l89_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l90_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l90_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l91_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l91_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l92_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l92_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l93_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l93_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l94_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l94_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l95_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l95_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300
queue=overnight_queue name=q_a3_l96_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l96_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle50_q_a3_n8192_l89_l96.md timeout=300

## Batch C: PP-58 SCS R5 rescue tau=0.50 (CPU)
Prereg: prereqs/2026-06-04_pp58_scs_tau050.md

queue=remote_cpu_queue name=pp58_scs_tau_sweep_d8_tau050_v1_n8192 script=experiments/exp_pp58_scs_tau_sweep_d8_tau050_v1_n8192.py prereg=prereqs/2026-06-04_pp58_scs_tau050.md timeout=10800

## Batch D: substrate_spectral_monitor_overfitting_v3 (CPU)
Prereg: prereqs/2026-06-04_spectral_monitor_v3.md

queue=remote_cpu_queue name=substrate_spectral_monitor_overfitting_v3_n4096 script=experiments/exp_substrate_spectral_monitor_overfitting_v3_n4096.py prereg=prereqs/2026-06-04_spectral_monitor_v3.md timeout=5400
