# Pre-registration: adversarial_aqsim_path_d_compose_v1_n4096

**Date**: 2026-05-31
**Anchor**: adversarial_aqsim_path_d_compose_v1_n4096
**Queue**: overnight_queue (GPU)
**Script**: experiments/exp_adversarial_aqsim_path_d_compose_v1_n4096.py
**PROT-018**: _n4096 binds N = 4096.
**PROT-019**: timeout_s = 14400 (floor).
**PROT-021**: per-seed checkpointing.

## Context

3 independent HARD_PASSes from today's session compose into one production question:
- v299 G7EXT: Path D no-ceiling depth=5 at 64N, N=4096
- v302 PP2ADV: c_quant/bits8 compression preserves KF-1/KF-2/KF-3 under adversarial
- v299 P4_AQSIM: a_query_sim defense defeats pattern_2+pattern_4 at N=4096
- v303 CPD: c_quant/bits8 x Path D composition at N=4096 HARD_PASS

Open question: do all 3 compose under a SINGLE UNIFIED WORKLOAD?

## Configuration

- N = 4096, M = 2048 (nominal), depth = 5, K_paths = 100
- 50 legitimate starts + 50 adversarial queries (codebook-collision, 50/50 interleave)
- c_quant/bits8 compression on W (4x)
- a_query_sim defense gate (threshold = 0.5)
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- Also measures on uncompressed W for differential isolation

## Primary metrics

1. **defense_rate**: fraction of adversarial queries rejected by a_query_sim gate
2. **acc_path_d_gated_compressed**: Path D acc on legitimate queries that PASS gate, on c_quant/bits8 W (3-way composition metric)
3. **acc_path_d_base_compressed**: Path D acc on legitimate queries, no gate, on compressed W (PP-2 x Path D from v1)
4. **fp_rate**: fraction of legitimate queries incorrectly rejected by gate
5. **comp_delta**: acc_base_uncompressed - acc_base_compressed (compression effect in isolation)

## Pre-registered thresholds

| Band | Condition |
|---|---|
| HARD-PASS | defense_rate >= 0.85 AND acc_path_d_gated_compressed >= 0.95 in 4/5+ seeds. Production stack coherent. |
| HARD-FAIL | acc_path_d_gated_compressed < 0.70 in majority (gate or compression breaks Path D) OR defense_rate < 0.50 in majority (defense degrades under compressed+interleaved). |
| MIDDLE-BAND | otherwise (partial; some conditions met). |

## Interpretation matrix

| defense_rate | acc_gated_comp | Interpretation |
|---|---|---|
| >= 0.85 | >= 0.95 | 3-way composition COHERENT; production stack validated |
| >= 0.85 | 0.70-0.95 | gate + compression degrade Path D mildly; engineering tuning needed |
| >= 0.85 | < 0.70 | gate filter is too aggressive OR compression + gate interact badly |
| < 0.50 | any | adversarial interleave degrades defense; adversarial attacks interfere with compression |

## Key theoretical note (formula self-test 3)

The a_query_sim gate uses codebook keys (not W) for the similarity check. Since
queries are uncompressed codebook vectors, compression of W does NOT change the
defense gate behavior. Therefore: comp_delta should be ~0 AND defense_rate should
match v299 G8 HARD_PASS result (1.0). Any deviation is a structural finding.

## Outcome plans

**IF HARD-PASS**: production deployment narrative is complete: c_quant/bits8 + Path D
+ a_query_sim defense compose coherently at N=4096, M=2048. Update cap_map:
"3-way composition (compression x Path D x adversarial defense) validated at N=4096."

**IF MIDDLE-BAND**: file characterization note identifying which interaction is weak.
Most likely: fp_rate high (gate rejects legitimate compressed queries). Tuning path:
lower defense threshold or use query renormalization before gate check.

**IF HARD-FAIL**: identify whether failure is compression-gate interaction (fp_rate high)
or defense degradation under interleaved load. File upstream routing to Strategy.

## Timeout estimate

Reference: path_d_adversarial_composition_v1_n4096 ~10s/seed on GPU.
This adds: compress W (trivial), second path_d_run on W_base (~10s).
Estimate: ~20s/seed x 5 seeds = 100s. Safety: ceil(1.5 * 100) = 150s.
PROT-019 floor dominates. **timeout_s = 14400**.

## N-suffix

PROT-018 binding: N_FULL = 4096 in script. Production config matches _n4096 suffix.
