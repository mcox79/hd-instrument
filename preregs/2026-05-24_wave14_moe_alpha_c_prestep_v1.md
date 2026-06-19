# Pre-registration: wave14_moe_alpha_c_prestep_v1

**Filed:** 2026-05-24  
**Script:** experiments/exp_wave14_moe_alpha_c_prestep_v1.py  
**Queue:** overnight_queue (GPU)  
**Timeout:** 3600s  

## Hypothesis

BSC outer-product associative memory (N=4096) has a measurable capacity threshold alpha_c = max{M : mean_cosine(recall) > 0.80} / N. This value (alpha_c_measured) is required for MoE SHIFT/PARTITION/SINGLE rebuild HARD-PASS conditions. Expected range from associative memory literature: alpha_c in [0.08, 0.25] for BSC variants.

## Method

- Single expert W[N x N] = (1/N) * sum_i v_i k_i^T (outer-product Hopfield rule)
- Sweep M in {200, 400, 800, 1600, 3200, 6400} at N=4096
- 5 seeds; measure mean cosine(recall, target) at each M
- Extract alpha_c_measured = largest M where mean_cosine > 0.80, divided by N
- Report 95% CI from seed variance

## Pre-registered bands

**HARD-PASS:**
- alpha_c_measured in [0.08, 0.25] (plausible BSC range)
- mean_cosine > 0.80 at M = alpha_c_measured * N
- mean_cosine < 0.50 at M = 3 * alpha_c_measured * N
- CI width < 0.10
→ Report alpha_c_measured + M_per_expert_recommended + M_total_recommended_k4 for MoE rebuild

**HARD-FAIL:**
- mean_cosine > 0.80 at ALL M including M=6400 (no saturation)
→ Substrate resolution insufficient; increase M_grid max or reduce N

**INSTRUMENTATION-FAIL:**
- Any seed produces NaN cosine, OR runtime > 45 min total
→ Re-design before continuing to MoE rebuild

**MIDDLE:**
- alpha_c_measured in range but CI width >= 0.10
→ Proceed with uncertainty note

## Output for downstream use

- `alpha_c_measured` (float): measured capacity fraction
- `m_per_expert_recommended` (int): 70% of alpha_c_measured * N
- `m_total_recommended_k4` (int): K=4, eta=0.80 aggregate target
- `mean_cosines` (dict[M -> float]): full retention curve

## Notes

- This is a MANDATORY PRE-STEP before the 3-arm SHIFT/PARTITION/SINGLE MoE rebuild
- Without alpha_c_measured, HARD-PASS conditions for the rebuild are ambiguous
- Literature alpha_c ~ 0.138 for standard Hopfield; BSC outer-product differs; empirical measurement is the load-bearing contribution
- Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]
