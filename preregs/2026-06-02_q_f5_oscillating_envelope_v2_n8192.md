# Pre-registration: q_f5_oscillating_envelope_v2_n8192

**Date:** 2026-06-02
**Script:** experiments/exp_q_f5_oscillating_envelope_v2_n8192.py
**Queue:** remote_cpu_queue
**N:** 8192 (PROT-018 _n8192 suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** MIDDLE_BAND at N=1024 (dft_snr=2.24, frac_osc=0.045; above HF but below HP)
**Timeout:** 14400s (Glauber O(N^2) heavy; 3 t_w x 100 replicas x 12 ratios)

## Hypothesis

Q-F5 Garcia-Lorenzana oscillating-amorphous overlay disambiguation at N=8192.
v1 (N=1024) MIDDLE_BAND. If CK pure-aging: HARD_FAIL. If Garcia-Lorenzana: HARD_PASS.

## Metrics

- `mean_dft_snr`: DFT peak SNR of age-collapsed correlator
- `mean_frac_osc`: variance fraction explained by oscillating envelope fit

## Thresholds

HARD-PASS: cell_A (dft_snr>=3.0) OR cell_B (frac_osc>=0.20) in >=3/5 seeds.
HARD-FAIL: mean_dft_snr<1.5 AND mean_frac_osc<0.05 (both HF in >=4/5 seeds).
MIDDLE: neither.
