# exp_dev queue routing: CYCLE 48 all-night burst (2026-06-04)

Queue at 0 after CYCLE 47 verdict batch (13 HP + 1 HF). Shipped 10 anchors.

## Shipment record

```
queue=overnight_queue name=q_a3_l113_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l113_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l113_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l114_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l114_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l114_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l115_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l115_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l115_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l116_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l116_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l116_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l117_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l117_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l117_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l73_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l73_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l73_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l74_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l74_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l74_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l75_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l75_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l75_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l76_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l76_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l76_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l77_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l77_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l77_n8192.md timeout=21600
```

## Justification
- Q-A3 N=16384: L=113-117 (rungs 94-98); prior L=112 HARD_PASS v379; 93-rung unbroken EXACT-1.0000 series; no ceiling found; ECC criterion satisfied (alpha=0.0061 << 0.138).
- Q-A3 N=8192: L=73-77 (rungs 54-58); prior L=72 HARD_PASS v379; 52-rung N=8192 series; no ceiling found; ECC criterion satisfied (alpha=0.0122 << 0.138); 2-N cross-N at L=73+ confirms both series.
- 10-anchor batch cap reached. PP-58 SCS tau sweep (R2 tau=0.01..0.20 sweep) deferred to next cycle.
- No padding: each anchor is directly justified by the open depth-ceiling question.

## PROT compliance
- PROT-018: all 10 anchors have _nN suffix binding (L=113-117 _n16384; L=73-77 _n8192). 0 violations.
- PROT-019: timeout=21600 >= 3600 floor for _n>=4096 anchors. PROT-019 floor applied.
- PROT-021: --skip-smoke applied. Pattern established across 93-rung series at N=16384 and 52-rung series at N=8192 with EXACT-1.0000 unanimous fidelity. Script --self-test passed 10/10.
- PROT-022: formula self-tests in each script: chain decode verify + alpha < alpha_c + GPU memory > 0.
- REMOTE VERIFY: 10/10 PASS (queue_add.sh exit-5 verify; entries confirmed in remote overnight_queue/queue.json).
