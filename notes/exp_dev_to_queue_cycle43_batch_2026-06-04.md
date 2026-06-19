# exp_dev Queue Routing: Cycle 43 Batch (v373)

**Date:** 2026-06-04
**Trigger:** USER-PRIORITY DISPATCH cycle 43 (10-anchor target). Routing notes LIFO.
**Cap_map version:** v373
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l84_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l84_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_q_a3_l84_l87_n16384_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l85_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l85_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_q_a3_l84_l87_n16384_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l86_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l86_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_q_a3_l84_l87_n16384_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l87_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l87_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-04_q_a3_l84_l87_n16384_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l48_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l48_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_q_a3_l48_l50_n8192_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l49_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l49_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_q_a3_l48_l50_n8192_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l50_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l50_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-04_q_a3_l48_l50_n8192_cycle43.md timeout=21600 --skip-smoke
queue=overnight_queue name=pp50_kappa3_sigma_g_extended_v5_n16384 script=experiments/exp_pp50_kappa3_sigma_g_extended_v5_n16384.py prereg=prereqs/2026-06-04_pp50_kappa3_sigma_g_extended_v5_n16384.md timeout=21600 --skip-smoke
queue=remote_cpu_queue name=substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384 script=experiments/exp_substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384.py prereg=prereqs/2026-06-04_substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384.md timeout=25200
queue=remote_cpu_queue name=pp58_scs_formula_test_d8_tau005_v1_n8192 script=experiments/exp_pp58_scs_formula_test_d8_tau005_v1_n8192.py prereg=prereqs/2026-06-04_pp58_scs_formula_test_d8_tau005_v1_n8192.md timeout=21600
```

## Rationale

- **Q-A3 L=84-87 N=16384** (B+C): continues N=16384 depth ladder past L=83. ECC criterion: per-stage alpha=0.0061 << alpha_c=0.138. EXACT fidelity expected.
- **Q-A3 L=48-50 N=8192** (D+E): continues N=8192 cross-N ladder past L=47. Same ECC argument at N=8192.
- **PP-50 v5 extended sigma_g** (F): extends prior HARD_PASS v4 (sg=0.83-2.0) to sg=1.0-5.0 to find true saturation. Discriminates log-linear continuation from saturation/fold.
- **gamma-vs-M SCS probe** (A): SCS vs RSB vs Lyapunov framework discriminator. HP ratio [0.50, 0.75] at both N confirms SCS. CPU-feasible, 50 cells, partial JSON per cell.
- **PP-58 SCS formula test** (G): direct test of gamma_SCS = (d + tau/d)/(1+tau) at N=8192. Independently measures d and tau; compares SCS prediction to empirical gamma.

## Ship verification

All 10: PROT-018 N-suffix verified; PROT-019 floor 21600s met; --self-test passed; VERIFIED in remote queues. 0 ship-name-collisions detected.
