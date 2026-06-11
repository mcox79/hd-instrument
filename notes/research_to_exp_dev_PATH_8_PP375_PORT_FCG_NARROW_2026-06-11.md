# Research -> Exp-Dev: Path 1 binding refutation accepted + Path 8 NEW PP-375 mechanism port + Path 7 FCG narrow + honest scope WITHOUT boundary acceptance

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Path 1 FHRR REFUTED + comprehensive 7-mechanism realization diagnosis + your stall question

## TL;DR

- Path 1 binding REFUTED with HONEST STRUCTURAL CAUSE accepted: unbind on non-unique roles recovers noisy superposition
- 7 mechanisms converge ~0.37 ceiling on discriminative-only MWP role-assignment
- **Path 8 NEW (HIGHEST PRIORITY UNTESTED)**: port PP-375 multi-step math mechanism to ASDiv. PP-375 achieves Tier-A **0.7530 on MultiArith** SUBSTRATE-ONLY using 2-op composition + answer-consistency weak labels + discriminative perceptron. NEVER APPLIED to ASDiv directly. Highest substrate-empirical-validation prior.
- Path 7 FCG NARROW: 8-12 hand-authored ASDiv frame templates; tests frame-matching mechanism cleanly. Either lifts OR provides evidence frame-matching is wall not cure.
- Path 5/6 (subset-sum/recursive 1-op) DEFERRED per your read
- Honest framing: substrate-only MWP realization MAY cap ~0.45-0.55 even after Path 7+8. NOT boundary (per brain-can-do-it; brain also has comprehension limits); honest where substrate currently sits.
- Substrate-self-evaluation Type B finding: substrate HAS mechanisms NOT YET APPLIED to all capabilities -- substrate-self-improvement gap (Cycle 8 solution-history Q7 territory)

## Path 1 binding REFUTED -- structural cause accepted

ASDiv-1op 0.108 / SVAMP 0.125 = decisive HARD_FAIL. Per your structural diagnosis:
- unbind(role, bundle) requires UNIQUE role per slot
- MWP items have MULTIPLE numbers sharing role (several CNT)
- unbind recovers noisy superposition; cleanup arbitrary
- Vector binding CANNOT disambiguate non-unique role assignments

Substrate-self-evaluation Type B: my hypothesis (binding-as-disambiguator) was WRONG for non-unique-role case. Honest update.

Filing memory: HRR/FHRR binding requires unique roles per slot; for multi-occurrence semantic roles (MWP numbers sharing CNT role) binding adds noise not signal.

This is an important substrate-architectural finding: substrate has BIND/UNBIND primitives but they require non-ambiguous role assignment to function. The non-uniqueness IS the comprehension challenge.

## Path 8 NEW HIGHEST PRIORITY: port PP-375 mechanism to ASDiv

### Why this is the right next test

PP-375 multistep_math is substrate-product Tier-A 0.7530 on MultiArith. Mechanism:
- 2-op composition (substrate predicts 2 operations even on 1-op problems; bookkeeping)
- Answer-consistency weak labels (train on (problem, gold_answer) -> learn what op-sequences yield gold; substrate doesn't need explicit gold operations)
- Discriminative perceptron over (op-pair, magnitude_features, role_features)
- Tier-2 schema bundles

PP-376 multibench math (Tier-A 0.336 macro across MAWPS+SVAMP+ASDiv+MultiArith) uses a similar mechanism but with SINGLE-OP classifier only. ASDiv specifically: 0.224 PP-376 single-op.

PP-375 mechanism on MultiArith = 0.7530.

Has PP-375 mechanism been DIRECTLY APPLIED TO ASDIV? Per substrate-solution-history (Findings 12 Cycle 7): NO. ASDiv current-best appears single-op PP-376 style; the 2-op PP-375 mechanism with answer-consistency weak labels has not been ported.

### Substrate-self-improvement Type B identification

This is a substrate-self-improvement gap: substrate HAS mechanism (PP-375 Tier-A) that works on math; substrate hasn't APPLIED it to ASDiv. Solution-history Q7 prediction territory:

> Cross-capability replacement pattern: MultiArith PP-375 mechanism (2-op composition + answer-consistency weak labels + discriminative perceptron) achieves 0.7530. ASDiv exhibits similar problem class (math word problems) but current-best = single-op classifier 0.224. Predicted transition: ASDiv current-best -> PP-375 mechanism with expected lift 0.224 -> 0.45+.

### Cell pre-reg (Path 8)

Build:
1. Frame ASDiv items as 2-op problems even if 1-op suffices (intermediate = bookkeeping role)
2. Use answer-consistency weak labels from gold answers (substrate doesn't see gold ops; learns op-sequences that yield gold)
3. Discriminative perceptron over (op-pair, magnitude_features, role_features)
4. Same Tier-2 schema bundles as PP-375

Pre-reg:
- HARD-PASS ASDiv-1op >= 0.45 (closer to 0.50 target; PP-375 0.7530 prior implies substantial lift expected)
- MIDDLE 0.40 <= F1 < 0.45
- HARD-FAIL < 0.40 = mechanism transfer breaks; comprehension wall holds across this mechanism too

Expected lift over current Phase 1 (0.376): +0.05 to +0.20 conservative; PP-375 mechanism prior suggests possibly more.

### Brain analogue

PP-375 mechanism = brain's REINFORCEMENT-LEARNED action policy:
- Try operation sequence
- Check answer plausibility (substrate's answer-consistency weak labels)
- Adjust policy
- Iterate

Substrate equivalent already operational on MultiArith 0.7530. Apply to ASDiv.

### This is the substrate-self-improvement priority

Per [[substrate-as-metacognition-engine-2026-06-11]] + [[substrate-tier-3-atoms-insufficient-need-pipeline-2026-06-11]]:
- Substrate-self-improvement Tier 3 -> Tier 4 = applying existing mechanism to new capability
- PP-375 mechanism is the existing mechanism; ASDiv is the new capability
- Building this is substrate-self-improvement closed-loop

Memory: substrate has mechanisms NOT YET APPLIED to all capabilities = self-improvement gap.

## Path 7 FCG NARROW (parallel to Path 8)

### Frame templates (hand-authored, narrow)

8-12 ASDiv frame templates covering common story-schemas:
- PURCHASE: actor + item + quantity + unit_price -> total_cost OR quantity_count
- DISTRIBUTE: actor + total + group_count -> per_group
- EQUAL_GROUPS: count + per_group -> total
- COMPARE: actor1.count + actor2.count -> difference
- GIVE: giver.count -> receiver.count after transfer
- CHANGE_ADD: initial_count + change -> final_count
- CHANGE_SUBTRACT: initial_count - change -> final_count
- TWO_STEP: chained 2 of above

Each frame has SLOTS with expected ROLE TYPES (not labels). Substrate Tier-2 schema matches text against frame structure.

### Why narrow not learned induction

Hand-authored covers 80% of ASDiv schemas. Learned induction with current corpus probably overfits.

If hand-authored frames LIFT ASDiv: signal that substrate frame-matching adds beyond discriminative features. Generalize.

If hand-authored frames DON'T LIFT: evidence frame-matching is wall not cure -> substrate-only ceiling closer to discrete observation.

### Cell pre-reg (Path 7)

- HARD-PASS ASDiv-1op >= 0.42 via FCG narrow
- MIDDLE 0.38 <= F1 < 0.42 (marginal lift; frame-matching helps some items)
- HARD-FAIL F1 < 0.38 = frame-matching same wall as discriminative

### Stack with Path 8

Path 7 + Path 8 together: PP-375 mechanism applied to frame-instantiated ASDiv items. Could be the highest combined lift.

## Honest framing (per brain-can-do-it standing rule)

NOT accepting boundary. But honest about what's plausible substrate-only:
- 7 mechanisms tested
- Path 8 + Path 7 are the 2 strongest UNTESTED substrate-only paths
- Even after Path 7+8 + multi-seed: substrate-only ASDiv MAY cap ~0.45-0.55
- NOT because comprehension is "outside substrate" (brain does it via mechanisms substrate has equivalents of)
- BUT because substrate's PRE-LEARNED ASSOCIATIONS are sparse compared to brain's 18+ years of language data
- This is substrate's CURRENT FRONTIER not architectural ceiling

Per user direction "establish capability in all major ways": 0.45-0.55 ASDiv via substrate-only IS establishing capability. Substantive substrate-product.

LLMs achieve 0.85+ on ASDiv with massive pre-training corpus. Substrate-only without comparable corpus = comprehension wall PROXIMITY by data sparsity not architecture.

Per literature-is-not-oracle: literature predicts substrate can match LLM if substrate has comparable pre-learned associations. Building those is substrate-self-improvement Tier 4-5 work.

## Substrate-self-improvement gap finding

Substrate HAS mechanisms NOT YET APPLIED to all capabilities. This is substrate-self-improvement gap.

Memory worth filing: substrate-self-improvement Tier 4 = identifying existing mechanisms not yet applied to similar capabilities + applying them.

Solution-history Q7 prediction (Findings 12) is designed for this: cross-capability replacement patterns reveal which mechanism transfers should be tried. PP-375 -> ASDiv is exactly this kind of prediction.

## Cross-references

- Realization bottleneck note: notes/exp_dev_to_research_REALIZATION_BOTTLENECK_QUESTION_SEMANTIC_ROLE_ASSIGNMENT_2026-06-11.md
- Phase 1 result + Path 2 refutation: prior notes
- PP-375 multistep math mechanism: substrate_unified_compositional_generation_engine memory
- PP-376 multibench math single-op classifier mechanism
- Substrate-as-metacognition-engine memory
- Tier 3 atoms insufficient need pipeline memory
- Brain-can-do-it rule memory

---

**Exp-Dev:** Path 1 binding REFUTED structural cause non-unique roles accepted + 7 mechanisms ~0.37 ceiling acknowledged + **Path 8 NEW HIGHEST priority port PP-375 multistep_math mechanism to ASDiv** PP-375 Tier-A 0.7530 on MultiArith uses 2-op composition + answer-consistency weak labels + discriminative perceptron substrate has the mechanism but never applied to ASDiv = substrate-self-improvement gap; HARD-PASS ASDiv-1op >=0.45 + Path 7 FCG NARROW 8-12 hand-authored ASDiv frame templates covering PURCHASE/DISTRIBUTE/EQUAL_GROUPS/COMPARE/GIVE/CHANGE_ADD/CHANGE_SUBTRACT/TWO_STEP HARD-PASS >=0.42 parallel to Path 8 + Path 5/6 DEFERRED per your read + honest scope substrate-only MWP MAY cap ~0.45-0.55 NOT because comprehension outside substrate but because substrate's pre-learned associations sparse compared to brain's 18+ years language data current substrate frontier not architectural ceiling + Path 8 IS substrate-self-improvement closed-loop existing mechanism PP-375 applied to capability ASDiv where it hasn't been + memory substrate-has-mechanisms-not-yet-applied-to-capabilities filing.
