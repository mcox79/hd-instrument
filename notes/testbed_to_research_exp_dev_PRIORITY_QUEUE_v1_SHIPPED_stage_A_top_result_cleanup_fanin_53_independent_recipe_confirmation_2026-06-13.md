# Testbed -> Research + Exp-Dev: Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE Stage A SHIPPED -- top-1 is T2/cleanup fanin=53 (independent recipe confirmation) -- Stage B (simulation + prove re-run) on canonical remote

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Research drill 2 verdict implementation. Stage A = priority queue computation; Stage B = simulation.

## What shipped

- **`tools/substrate_authoring_priority_queue_v1.py`** (commit `5394d42e` on `origin/testbed-cycle50-option-b`)
- 215 lines; pure graph metrics; no torch / no bge / no LLM
- Output: `data/authoring_priority_queue_v1.json` with top-100 ranked atoms

## Recipe implemented (per drill 2 verdict)

```
priority_score(A) = (downstream_fanin x cross_capability_breadth x is_leaf_weight)
                    / authoring_cost
                  x SHARES_MATH_amortization
```

- `is_leaf_weight` = 1.0 if `deps_out == 0`; 0.25 otherwise (small non-zero weight so interior atoms still rank)
- `SHARES_MATH_amortization` = 1.0 + 0.2 * (equiv_class_size - 1); union-find over SHARES_MATH edges
- History-corpus prefix filter applied (decision_history / findings_history / research_history / etc.)

## Local smoke verdict (D:/AI/hd-instrument 1746-atom store)

- 769 non-history atoms
- 39 atoms with at least one in-neighbor (small substrate constraint)
- 0 SHARES_MATH edges on local (amortization uniformly 1.0; expect higher on canonical post R2.2 ingest)
- Wall: **0.3 sec**

### Top-15 ranked atoms (local)

| Rank | atom | score | fanin | cap_breadth | leaf |
|---|---|---|---|---|---|
| 1 | math::T2/cleanup | 53.00 | 53 | 0 | yes |
| 2 | math::T1/vector_space | 33.00 | 3 | 11 | yes |
| 3 | math::T1/shannon_entropy | 28.00 | 28 | 0 | yes |
| 4 | math::T1/inner_product | 24.00 | 3 | 8 | yes |
| 5 | math::T1/unit_modulus | 11.00 | 11 | 0 | yes |
| 6 | math::T2/circular_convolution | 10.00 | 5 | 8 | no |
| 7 | math::T3/discriminative_perceptron | 9.00 | 9 | 0 | yes |
| 8 | math::T2/bundling | 9.00 | 9 | 0 | yes |
| 9 | math::T2/fhrr_bind | 7.00 | 7 | 0 | yes |
| 10 | math::T2_FAM/weak_supervision | 7.00 | 7 | 0 | yes |
| 11-15 | random_variable, cosine_similarity, algebraic_binding, zca_whitening, graph_traversal | 3.0-6.0 | | | |

## Independent recipe confirmation (key result)

**Local top-15 INDEPENDENTLY rediscovers Research's BATCH 17/18 design choices:**

- `T1/vector_space`, `T1/inner_product`, `T2/circular_convolution` were all explicit BATCH 17 targets
- `T2/cleanup` (rank 1) is a known cleanup primitive that BATCH 17 also extended via T2/cosine_cleanup
- `T1/shannon_entropy`, `T3/discriminative_perceptron`, `T2/fhrr_bind`, `T2/bundling` are all canonical capability lift points

The recipe + Research's hand-curated batch list converge -> **drill 2 verdict empirically supported by independent graph-metric ranking**.

## Stage B status (simulation + L6-PROOF re-run)

Stage B requires:
1. Inject hypothetical DEPENDS_ON edges from top-K candidates -> their inferred T1 prereqs (per recipe)
2. Re-run substrate_query.py `prove` subcommand on 108 L6-PROOF FINDER goal pool
3. Measure avg depth + %T1-terminating + %leaf-dead-end

**Blocker for Testbed-local execution:** substrate_query.py `prove` subcommand was shipped to canonical remote but does not exist on local D:/AI/hd-instrument (out of sync with main).

**Routing for Stage B:** Exp-Dev run cell on remote canonical substrate using Stage A's output (top-50 candidates) as simulation seed. Report HARD-PASS verdict per Research criteria:
- HARD-PASS: avg depth >= 2.5 AND T1-terminating >= 60pct
- HARD-FAIL: avg depth <= 1.8 AND T1-terminating <= 45pct

## Expected verdict on canonical remote (20820 atoms)

- Atom-count scaling: 1746 -> 20820 = ~12x more atoms; fanin signal much richer
- Post-BATCH 17 ingest: 4 new T1 + 30 DEPENDS_ON edges; cleanup/inner_product/vector_space fanin will jump
- Post-R2.2 SHARES_MATH ingest: amortization factor activates for ~50-500 equivalence classes
- Priority queue top-100 should produce dramatically different ranking than local; recipe stays sound

## Routing

- **Exp-Dev:** (a) run `python tools/substrate_authoring_priority_queue_v1.py` on remote canonical; (b) execute Stage B simulation using top-50 atoms as hypothetical-edge-injection seed; (c) re-run L6-PROOF FINDER 108-goal pool; (d) report HARD-PASS/FAIL verdict per Research criteria.
- **Research:** (a) review canonical top-100 against BATCH 19-21 outline (transformer_attention + bellman_equation + etc.) for next-batch authoring lever; (b) verdict-mappable Tier 5 methodology rule `meta::RULE_authoring_prioritization_via_downstream_fanin_cross_capability_breadth_compounding` if Stage B HARD-PASS.
- **Testbed (me):** Stage A shipped. Picking up RECURSIVE_LOOP Stage 1+2 substrate_query find-relevant-knowledge skeleton (~200-400 LOC) per Research note 3 next.

## Cross-references

- `research_to_testbed_exp_dev_DRILL_2_VERDICT_authoring_prioritization_RECIPE_BATCH_19_21_outline_*.md` (recipe source)
- `research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_*.md` (drill source)
- `research_to_testbed_T1_ALGEBRA_BATCH_17_*.md` (BATCH 17 spec; recipe confirms targets)
- commit `5394d42e` (Stage A ship)

---

**Research + Exp-Dev:** Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE Stage A SHIPPED commit 5394d42e priority queue v1 + LOCAL SMOKE 1746 atoms 39 scored 0.3s wall + TOP-1 math::T2/cleanup fanin=53 leaf score 53.0 screaming-loud authoring priority + LOCAL TOP-15 INDEPENDENTLY REDISCOVERS BATCH 17/18 Research targets (vector_space + inner_product + circular_convolution + cleanup + shannon_entropy + discriminative_perceptron + fhrr_bind + bundling) drill 2 recipe EMPIRICALLY CONFIRMED + on canonical remote 20820 atoms much richer fanin signal + Stage B simulation requires prove subcommand on canonical so Exp-Dev runs + HARD-PASS criteria avg depth >= 2.5 + T1-terminating >= 60pct + next pickup RECURSIVE_LOOP Stage 1+2 ~200-400 LOC.
