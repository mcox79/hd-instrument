# Research -> Testbed + Exp-Dev: L6-PROOF substrate_query.py prove subcommand -- USER-GOAL-ALIGNED HIGHEST PRIORITY work item -- substrate-as-differentiable-theorem-prover ship plan

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close)
**Re:** Theorem-prover drill HARD-PASS verdict (P_deflated 0.45); substrate already has 70-80pct of NTP/NeuralLP/RNNLogic math surface; USER goal "substrate understands its own mathematics" direct alignment

## TL;DR

Research drill returned HARD-PASS verdict on substrate as differentiable theorem-prover surface. Substrate's current scaffold (algebra_dict.axioms + DEPENDS_ON + SHARES_MATH + FHRR bind/unbind + PP-410 two-vector composite) is ALREADY 70-80pct of the NTP/NeuralLP family proof-surface. **L6-PROOF intervention**: backward-chaining proof unfolder via substrate_query.py prove subcommand. Maps directly onto USER goal.

Direct quote USER directive: "we want to get substrate to a point that it understands its own mathematics. it needs the background to do that"

L6-PROOF closes this gap categorically (LLM categorical gap across 8 dimensions per drill matrix).

## Ship plan -- 3 phases

### PHASE 1: Algebra corpus (Research + Testbed)

- Research T1 algebra-dict backfill BATCH 01-04 SHIPPED (40 atoms / 28pct of 144 target covering linear algebra + probability + info theory + topology + analysis)
- BATCH 05+ on demand (categorical / algebraic structures / differential calculus / numerical linear algebra)
- Testbed ingest BATCH 01-04 when bandwidth allows (Cycle 51+ corpus expansion)
- Need: algebra_dict.is_axiom = True flag on terminal axiom atoms (per drill cell spec)

### PHASE 2: substrate_query.py prove subcommand (Testbed or Exp-Dev)

Per drill cell spec (`exp_substrate_proof_unfolder_backward_chaining_axiom_DEPENDS_ON_v1`):
- New subcommand: `substrate_query.py prove <goal_atom> [--max-depth=5] [--cos-floor=0.30]`
- Reads goal_atom.algebra_dict.axioms; recursively unfolds via DEPENDS_ON edges (backward chaining)
- At each step: FHRR unification `cos(bind(goal_role, atom_filler), bind(rule_role, rule_filler)) > 0.30` (substrate-native soft-unification floor per PP-410 alpha=0.5 robust plateau)
- Aggregates proof scores via product of unification cosines along proof path (NTP-style max-pool over alternatives, multiplication along chain)
- Stops at axiom-marked leaves (`algebra_dict.is_axiom = True`) or max_depth
- Returns: structured JSON proof_path + proof_score + UNPROVABLE-no-axiom-chain when no path exists

### PHASE 3: Pre-reg verification cell (Exp-Dev)

5 pre-registered test goals:
- G1: `prove orthogonality_implies_zero_inner_product` (depth-2)
- G2: `prove KL_divergence_non_negative` (depth-3 jensen + log_concavity)
- G3: `prove mutual_information_non_negative` (depth-4 KL + chain_rule)
- G4: `prove Cauchy_Schwarz_in_inner_product_space` (depth-3 inner_product + non_negativity)
- G5 (negative control): `prove Riemann_hypothesis` (must return UNPROVABLE-no-axiom-chain)

HARD-PASS: >=4/5 correct + G5 correctly UNPROVABLE
MIDDLE: 2-3/5 + G5 correct (corpus insufficient, BATCH 05+ needed)
HARD-FAIL: <=1/5 OR G5 spurious proof (backward chaining wrong for substrate)

## Why this is highest-priority USER-goal work

1. **Direct USER-goal mapping**: macro 0.70 substrate-self-knowledge benchmark answers "what does substrate know?". L6-PROOF answers "WHY does substrate know?". Step-change from retrieval to derivation.

2. **Substrate-product positioning leap**: per drill matrix substrate-vs-GPT-4-vs-Lean-Copilot, substrate L6-PROOF wins on 8 categorical dimensions (audit interface + discrete proof skeleton + closed-form axiom field + FHRR unification + SHARES_MATH lemma reuse + honest UNPROVABLE + auditable JSON proof + no external verifier required).

3. **Compounds with HP_v1+ macro work**: L6-PROOF is orthogonal lever (not a competing C-axis lever). Macro work and proof-surface work run in parallel without cross-axis interference (same additive-composition pattern that delivered 7 mechanism classes Cycle 51).

4. **L3 DisCoCat coalgebraic unification**: per drill cross-thread synthesis, L6-PROOF + L3 DisCoCat unify under single bialgebraic semantics (already pre-registered Cycle 52 work). L6-PROOF activation accelerates L3 deployment.

## Cost / timeline

- PHASE 1: Research BATCH 05+ as needed; Testbed ingest BATCH 01-04 (~3-5 hours total ingest)
- PHASE 2: Testbed or Exp-Dev `substrate_query.py prove` implementation (~1-2 days, ~200-400 lines Python; well-scoped)
- PHASE 3: Exp-Dev pre-reg verification cell (~3-5 hours CPU + analysis)

Total: ~3-5 days from now to L6-PROOF HARD-PASS verdict.

## Priority justification

L6-PROOF is HIGHER PRIORITY than:
- Q33/Q34/Q37 A-axis advanced description enrichment (still queued)
- Phase-6 corpus ingest beyond T1 algebra batches (still queued)
- 28-atom math-primitive Option F hybrid ingest (still queued)
- Cycle 52 NL-to-HRR parser SNR plan (DEFERRED per prior coordination)

L6-PROOF is EQUAL PRIORITY to:
- Path-to-HP_v1+ Q40 SUPERSEDES + Q16/Q17/Q53 + G-axis refinement (both close-path-additive)
- T1 algebra-dict backfill (precondition for L6-PROOF + USER goal)

L6-PROOF is LOWER PRIORITY than:
- LFS migration P0.3 (push state restoration is blocking everything; user authorization pending)

## Routing

- **Testbed**: PHASE 2 subcommand implementation candidate (substrate-query.py extension); alternative Exp-Dev
- **Exp-Dev**: PHASE 3 pre-reg verification cell + alternative PHASE 2 owner; coordinate with Testbed on ownership split
- **Research**: BATCH 05+ T1 algebra-dict authoring on demand; standing for verdicts

## Cross-references

- notes/research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md (drill source)
- notes/research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_01-04_*.md (corpus precondition)
- notes/research_to_testbed_exp_dev_CYCLE_51_CLOSE_SYNTHESIS_*.md (Cycle 51 close + path-to-HP_v1+)
- memory `substrate-cycle-51-close-HP-v1-0-70-HARD-PASS-macro-0-7013-2-days-early-7-mechanism-classes-2026-06-12`
- memory `substrate_algebra_coverage_gap_two_populations_backfill_144_T1_2026-06-12`
- memory `substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12`

---

**Testbed + Exp-Dev:** L6-PROOF substrate_query.py prove subcommand HIGHEST-PRIORITY USER-GOAL-ALIGNED + drill HARD-PASS substrate already 70-80pct of NTP/NeuralLP math surface + 3-phase ship plan PHASE 1 algebra corpus BATCH 01-04 shipped Testbed ingest BATCH 05+ on demand + PHASE 2 substrate_query.py prove subcommand backward-chaining FHRR unification floor 0.30 + PHASE 3 pre-reg verification 5 goals G1-G4 PASS G5 UNPROVABLE + LLM categorical gap 8 dimensions + USER goal direct mapping macro answers what substrate knows L6-PROOF answers WHY + compounds orthogonally with HP_v1+ macro work + L3 DisCoCat coalgebraic unification candidate + 3-5 days timeline to HARD-PASS verdict + USER full-auto continuing.
