# Pre-registration: pp47_pp49_counterfactual_abduction_composition_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: pp47_pp49_counterfactual_abduction_composition_v1

## Scientific question
Does place-field encoding (PP-47) compose with counterfactual abduction (PP-49) via rank-1
substitution? W_cf = W - xi_k xi_k^T/N + xi_{k+SHIFT} xi_{k+SHIFT}^T/N.

## Hard-pass (pre-registered)
HP1: baseline cosine >= 0.85 (place-field retrieval at N=4096)
HP2: cf cosine >= 0.70 (counterfactual pattern retrieved)
HP3: consistency >= 0.85 (original pattern NOT retrieved from cf query)

## Hard-fail (pre-registered)
HF1: cf cosine < 0.40 (no abduction)
HF2: consistency < 0.40 (original still dominates cf query)

## Middle band
2/3 HP conditions met

## Smoke result
MIDDLE_BAND: 2/3 conditions met (N=1024 smoke).
HP1 fails at N=1024 (baseline 0.72 vs 0.85). Small-N effect: place-field retrieval
improves substantially at N=4096. HP2=0.97, HP3=0.97 both pass.
Walk-back gate applied: FULL seeds increased from 5 to 7.

## Production config
N=4096, SEEDS=[7,17,23,31,41,53,67], K_LOCS=50, N_CF_QUERIES=20

## Timeout estimate
~420s (1.5 * 5s_smoke * 16x_N_scale * 3.5x_seeds)
