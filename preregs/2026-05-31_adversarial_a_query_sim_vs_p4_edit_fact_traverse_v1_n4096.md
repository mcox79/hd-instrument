# Pre-registration: adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096

**Date**: 2026-05-31
**Anchor name**: adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096
**Script**: experiments/exp_adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096.py
**Queue**: overnight_queue (cloud Lambda A10 GPU)
**Total cells**: 5 (1 M-value x 5 seeds)
**PROT-018**: _n4096 suffix binds N = 4096
**Authorization**: user-authorized Lambda batch v2 (commit 2fae636)

## Hypothesis

The a_query_sim defense (cosine similarity threshold >= 0.5 against stored keys)
is GENERAL: it defeats not only codebook-collision (G8_HARD_PASS) but also the
p4 edit-fact-traverse attack, achieving defense_rate >= 0.95 AND fp <= 0.05
at the same operating point (N=4096, M=2048).

## Configuration

- N: 4096 (PROT-018 binding)
- M: 2048 (same operating point as G8)
- Seeds: [7, 17, 23, 31, 41]
- Attack pattern: p4 edit-fact-traverse (same pattern function as U2 adversarial probing)
  - Edit n_edit=32 facts in-place (Hebbian rank-1 update: remove old, add new)
  - Query original keys post-edit; attack goal = recover pre-edit (old) values
- Defense: a_query_sim (threshold=0.5, identical to G8)
- Defense measurement: fraction of p4 queries where defense rejects OR returns new value
- FP measurement: fraction of post-edit legitimate queries rejected OR returning old value

## p4 attack mechanics

1. Select n_edit key-value pairs from stored facts
2. Compute new W' = W - (old_val x key^T)/N + (new_val x key^T)/N
3. Query original keys against W' -- attacker expects old_val back
4. Undefended substrate returns NEW value (Hebbian edit works correctly)
5. a_query_sim may additionally reject queries (threshold check)

Note: since edited keys are still valid stored keys, similarity to stored keys
remains high (> 0.5); the defense is expected to ACCEPT queries and rely on
substrate edit semantics. Defense success = substrate + defense returns new
value, not old value.

## Pre-registered bands

**HARD-PASS (HP)**:
  defense_rate >= 0.95 AND fp_rate <= 0.05 across all 5 seeds.
  Interpretation: a_query_sim is general; D7 edit-log-replay engineering
  motivation reduces substantially.

**HARD-FAIL (HF)**:
  defense_rate < 0.50 OR fp_rate > 0.20 at any seed.
  Interpretation: a_query_sim is codebook-collision-specific; D7 engineering
  remains justified.

**MIDDLE-BAND (MB)**:
  Neither HP nor HF.
  Next step: determine whether partial defense is from a_query_sim mechanism
  or from substrate Hebbian edit semantics alone (compare baseline_defense_rate).

## Calibration note

G8 showed def=1.000 at N=4096 for codebook-collision. P4 is a different attack
(edit-based, not collision-based). The substrate edit semantics already provide
natural protection (baseline_defense_rate field measures this). HP at 0.95 is
appropriate as the combined defense should at minimum match substrate semantics.

## Timeout estimate

5 seeds, M=2048, N=4096. Comparable to G8 which ran in ~3-4 min.
Formula: 1.5 * 240s * (4096/4096)^1.0 * (5/5) = 360s
Timeout: 900s (15 min, generous margin for p4 scenario overhead).

## Strategic value

If PASS: a_query_sim is a general-purpose adversarial defense mechanism; P6
in the handoff (D7 edit-log-replay engineering) is de-prioritized.
If FAIL: a_query_sim is pattern-specific; D7 engineering remains a separate
and necessary work item for the adversarial robustness claim.

## N-suffix binding

_n4096 suffix: production N = 4096. Confirmed in script: `N_FULL = 4096`.
Smoke runs at N_SMOKE = 1024.
