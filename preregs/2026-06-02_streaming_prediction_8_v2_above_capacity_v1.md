# Pre-registration: streaming_prediction_8_v2_above_capacity_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: streaming_prediction_8_v2_above_capacity_v1

## Scientific question
Does the windowed Hopfield policy outperform unbounded accumulation in the above-capacity
regime? v1 was below-capacity (both policies work -> no discrimination). v2 probes
alpha_unbounded_late >> alpha_c while alpha_window < alpha_c.

## Hard-pass (pre-registered)
HP-A: mean_fidelity_windowed >= 0.70 (windowed policy works at alpha_window < alpha_c)
HP-B: late_advantage = fid_windowed_late - fid_unbounded_late > 0.20
HP-C: newest_fidelity >= 0.80 (most recent sequence item recoverable)

## Hard-fail (pre-registered)
HF-A: mean_fidelity_windowed < 0.40 (windowed policy fails)
HF-B: late_advantage < 0 (unbounded beats windowed)

## Middle band
2/3 HP conditions met

## Smoke result
HARD_PASS: all 3 HP conditions met (N=1024 smoke, 2 seeds).
mean_fid_w=1.000, late_adv=+0.261(>0.2), newest=1.000.

## Production config
N=1024, WINDOW_SIZE=120, T_TOTAL=600, SEEDS=[7,17,23,31,41]
alpha_window=0.117 < alpha_c=0.138; alpha_unbounded_late=0.586 >> alpha_c

## Timeout estimate
~83s (1.5 * 11s * 2x_T * 2.5x_seeds)
