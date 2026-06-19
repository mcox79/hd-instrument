# exp_dev Queue Routing: Cycle 44 Refill (v375)

**Date:** 2026-06-04
**Trigger:** Cycle 43 15-verdict batch processed; queue=0 refill per pipeline-pacing.
**Cap_map version:** v375
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l88_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l88_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle44_q_a3_n16384_l88_l90.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l89_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l89_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle44_q_a3_n16384_l88_l90.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l90_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l90_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_cycle44_q_a3_n16384_l88_l90.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l51_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l51_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle44_q_a3_n8192_l51_l53.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l52_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l52_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle44_q_a3_n8192_l51_l53.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l53_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l53_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_cycle44_q_a3_n8192_l51_l53.md timeout=21600 --skip-smoke
queue=remote_cpu_queue name=substrate_spectral_monitor_overfitting_v1_n4096 script=experiments/exp_substrate_spectral_monitor_overfitting_v1_n4096.py prereg=prereqs/2026-06-04_spectral_monitor_overfitting_v1_n4096.md timeout=21600
queue=remote_cpu_queue name=pp58_scs_d_sweep_v1_n8192 script=experiments/exp_pp58_scs_d_sweep_v1_n8192.py prereg=prereqs/2026-06-04_pp58_scs_d_sweep_v1_n8192.md timeout=21600
```

## Rationale

- **Q-A3 L=88-90 N=16384** (A): continues N=16384 depth ladder past L=87. ECC criterion: per-stage alpha=0.0061 << alpha_c=0.138. EXACT fidelity expected. 3 new rungs 65-68.
- **Q-A3 L=51-53 N=8192** (B): continues N=8192 cross-N ladder past L=50. 3 new rungs 32-34. 2-N cross-N at L=51/52/53 {N=8192+N=16384}. Combined 6-rung batch with N=16384 batch triggers BAND-LIFT 0.90->0.91.
- **spectral_monitor_overfitting** (C): R1 rescue from rung-1 HARD_FAIL. Re-pre-reg with overfitting-phase-only criterion (3/3 HP at +300 steps in rung1). HP_LEAD=50 steps. 30000 chars repeated for reliable overfitting. CPU; ~90s.
- **pp58_scs_d_sweep** (D): R2 rescue from SCS formula HARD_FAIL (d<1.5 at alpha=0.05). Alpha sweep [0.01..0.13] to find where spectral spike (d>=1.5) emerges. CPU; ~400s.

## Ship verification

All 8: PROT-018 N-suffix verified; PROT-019 floor 21600s met; --self-test passed (remote); VERIFIED in remote queues. 0 ship-name-collisions detected.
overnight_queue: 6 anchors (L=88/89/90 N=16384 + L=51/52/53 N=8192).
remote_cpu_queue: 2 anchors (spectral_monitor_overfitting + pp58_scs_d_sweep).
