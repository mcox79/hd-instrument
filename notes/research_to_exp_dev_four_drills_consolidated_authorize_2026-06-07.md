# Research -> Exp-Dev: 4 negative-finding drills consolidated routing (user authorized)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** User directive "authorized on your recommendations" after 4 drills landed.

## 1. SQL AVG formula bug fix (HIGHEST PRIORITY; 30 min CPU)

The cycle 155 SQL hybrid aggregation MID where AVG returned 100% error is a FORMULA BUG,
not a substrate algebra limit. Off-by-N division in HD bundle energy estimator: divides
by N when input vectors are already unit-norm. ||bundle||^2 approximates COUNT directly;
dividing again by N=4096 gives 0.012 instead of 50, which is 99.98% error.

Method: fix the formula in the SUM and AVG estimators (remove the extra /N when inputs
are pre-normalized); rerun cycle 155's sql_hybrid_aggregation cell.

HARD-PASS: AVG relative error < 5% (matches theory at O(1/sqrt(N)) ~ 1.6% at N=4096).
HARD-FAIL: AVG error still > 50% (formula fix didn't help; substrate algebra IS the
limit; revert to DuckDB-hybrid framing).

Wall: 30 min CPU.

Decision impact: if HARD-PASS, the cycle 155 MID retroactively upgrades to HP. Substrate
handles COUNT, SUM, AVG natively (not just COUNT/SUM with AVG needing DuckDB). The cap_map
row gets a meaningful upgrade.

## 2. CELL-3 distillation alternative pre-test (skip distillation if bge-small works)

The CELL-3 distillation alternatives 2x drill recommended bge-small@d=30 as top alternative
(P_actionable=0.39). If bge-small@d=30 outperforms the 22M distilled student on retrieval
F1, we skip the distillation entirely and use bge-small as the production encoder for the
v1 inference path.

Method: measure bge-small@d=30 retrieval F1 on HotpotQA test set (50-100 questions);
compare to the existing distilled student's projected F1 (using val_cos=0.79 as the
proxy).

HARD-PASS: bge-small@d=30 F1 >= distilled student F1 (likely outcome). Recommend skipping
CELL-3 distillation engineering for v1.

HARD-FAIL: bge-small@d=30 underperforms distilled student by >= 10% F1. Authorize InfoNCE
loss pivot for CELL-3 (already partially routed).

Wall: 30 min CPU.

## 3. Predicate routing adaptive rescue (1-2 hours CPU)

The predicate routing scaling limit drill's top rescue is ADAPTIVE ROUTING (P=0.65):
rare predicates stay on HD path with full algebraic certificates; common predicates fall
back to inverted index.

Method: extend cycle 155's predicate_ratio_audit setup with adaptive routing logic:
- Threshold T = 5% selectivity (predicates with frequency below T stay on HD; above T
  fall back to inverted index)
- Run the same 8-predicate / 200-fact KB
- Measure recall@10 across selectivities {1%, 3%, 5%, 7%, 10%, 15%, 20%, 30%}

HARD-PASS: adaptive routing maintains recall@10 >= 0.90 across ALL selectivities (not
just <= 5%). Product claim upgrades from "rare predicates only" to "full recall across
all selectivity with 2-layer routing."

HARD-FAIL: adaptive routing improves recall<= 0.05 above flat routing (no meaningful
fix; predicate scaling limit is fundamental).

Wall: 1-2 hours CPU.

## 4. Composite indexing rescue (parallel to #3; 2-4 hours CPU)

Second-rank rescue: composite indexing (bind predicate + subject together as joint key).
Reduces bundle interference by partitioning facts by joint predicate-subject identity.

Method: same predicate audit setup with composite (predicate, subject) keys instead of
predicate alone. Measure recall@10 across selectivities.

HARD-PASS: composite recall@10 >= 0.90 at 20%+ selectivity (where flat predicate routing
hard-fails).
HARD-FAIL: marginal lift.

Wall: 2-4 hours CPU.

## 5. Substrate composition regime pre-tests (already routed separately)

Pre-test A (K-sweep brute-context degradation) and Pre-test B (compositional questions
graph-traversal vs dense) are routed separately at
notes/research_to_exp_dev_substrate_composition_regime_pretests_2026-06-07.md. Continue
on that schedule.

## 6. Two Testbed follow-ons (already routed separately)

1M substrate scale test (~20 min local GPU) and HotpotQA Tier-1 head-to-head (~30 min
local GPU) are routed at
notes/research_to_exp_dev_two_testbed_followon_fast_2026-06-07.md.

## Sequencing recommendation

Tier A (CPU, <2 hours, run in parallel):
- #1 SQL AVG formula bug fix (highest priority; 30 min; may unlock free native AVG)
- #2 CELL-3 bge-small@d=30 pre-test (30 min; may simplify Phase 0.5 deployment)
- #3 Predicate adaptive routing (1-2 hours; engineering rescue)
- Composition regime Pre-test A (2-3 hours; from separate routing)

Tier B (3-4 hours CPU):
- #4 Composite indexing (2-4 hours; second-rank rescue)
- Composition regime Pre-test B (3-4 hours; from separate routing)

GPU (local; 20-30 min each):
- Two Testbed follow-ons (1M substrate + HotpotQA Tier-1)

Total wall time if parallelized: ~3-4 hours; $0 cloud.

## Cross-references

- SQL aggregation extension 2x drill: notes/research_drill_substrate_aggregation_extension_2x_2026-06-07.md
- SQL aggregation handoff: notes/exp_dev_handoff_research_aggregation_extension_2x_2026-06-07.md
- CELL-3 distillation alternatives 2x: notes/research_drill_cell3_distillation_alternatives_2x_2026-06-07.md
- Predicate routing scaling limit 2x: notes/research_drill_predicate_routing_scaling_limit_2x_2026-06-07.md
- Composition regime 2x: notes/research_drill_substrate_composition_regime_2x_2026-06-07.md
- Composition pre-tests routing: notes/research_to_exp_dev_substrate_composition_regime_pretests_2026-06-07.md
- Testbed follow-ons routing: notes/research_to_exp_dev_two_testbed_followon_fast_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all per sequencing above. Apply HARD-PASS / HARD-FAIL decision
rules autonomously per cell. File synthesis when batches complete.

#1 (SQL AVG formula fix) is highest priority because it's a 30-min bug fix that could
retroactively upgrade cycle 155 MID to HP. Run that first.
