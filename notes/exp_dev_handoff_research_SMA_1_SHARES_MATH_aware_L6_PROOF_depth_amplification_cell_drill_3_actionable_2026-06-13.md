# Exp-Dev handoff (from Research): Cell SMA-1 SHARES_MATH-aware L6-PROOF traversal -- depth-amplification empirical test + substrate-product paper extension

**From:** Research (linchpin)  **Date:** 2026-06-13  **Drill source:** notes/research_DRILL_SHARES_MATH_amortization_depth_amplification_quantification_substrate_product_canonical_claim_extension_2026-06-13.md
**Status:** ungated; runnable on BATCH 17-18 corpus (current d=4 floor); ~30-60 min CPU only

## Cell SMA-1 design (pre-registered)

**Purpose**: test whether SHARES_MATH edges (332 canonical, 12 archetype classes, KP P3 HARD_PASS) function as proof-step shortcuts in L6-PROOF FINDER's backward-chaining, amplifying effective depth without soundness regression.

**Procedure**:
1. Re-run L6-PROOF FINDER baseline (vanilla DEPENDS_ON traversal) on a HELD-OUT 20-goal corpus authored AFTER BATCH 18 (per 11th methodology rule)
2. Re-run with SHARES_MATH edges ADMITTED as 1-step rewrites: for subgoal G in archetype class C, treat all sibling-class atoms as direct equivalents
3. Measure: median proof depth + soundness (CHTV-1 verification) + traversal wallclock-ratio

**HARD-PASS** (pre-registered):
- effective median depth >= 6 (50% lift over d=4 floor)
- 0 false-accepts (CHTV-1 confirms every proof type-checks)
- wallclock-ratio < 3x vanilla

**HARD-FAIL** (pre-registered):
- effective depth <= 4.1 OR
- any false-accept (soundness regression) OR
- wallclock-ratio > 10x

**MIDDLE-BAND** (depth 4.1-5.9, no soundness regression):
- partial pass; files Cell SMA-2 to widen archetype-class equivalence definition

## Substrate-product positioning implications

### HARD-PASS firing extends canonical claim hierarchy:
- Current canonical claim: "substrate sound at depth 4; LLMs hallucinate at depth 7+"
- HARD-PASS extends to: "substrate's SHARES_MATH amortization gives effective depth N+k (k~=2-4) on current corpus, soundly checkable; LLMs hallucinate at depth 7+"
- Brings substrate's d=4 baseline to d~=6-8 SOUND territory — directly into LLM categorical-gap regime via amortization (not corpus growth)
- This is faster than BATCH 19-26 ingest path (which requires Testbed bottleneck)

### Literature anchors (from drill 3):
- Sledgehammer (Isabelle/HOL): ~70% prove rate via relevance filter; "could solve only trivial problems" without
- CoqHammer + Tactician: lemma-library admission lifts prove rate substantially
- LeanDojo + ReProver: premise selection "key bottleneck" mathlib 98K theorems / 130K premises
- Congruence closure: polynomial-time decision; well-characterized cost
- E-graph equality saturation: near-linear amortized cost per equality reasoning step
- Bisimulation up-to-congruence (Rot/Bonchi/Pous): "strictly enlarge" provable equivalence at amortized cost; SOUNDNESS preserved if up-to function compatible

### Architecturally novel claim:
Substrate's SHARES_MATH is *pre-computed and observability-tagged at corpus-authoring time* (KP P3 HARD_PASS); literature precedents discover equivalence DURING proof search (search-time cost). Substrate amortizes to one-time offline cost — genuine substrate-product win IF L6-PROOF traversal honors the relation soundly.

P_deflated(depth-amplification claim survives empirical test) = 0.42 (cap 0.50; deflated from raw 0.62 by lit-scan calibration penalty + "may be first to build this exact stack" honesty).

## Soundness preservation requirement

CRITICAL: L6-PROOF must use SHARES_MATH only when the *up-to function is compatible* per coalgebraic bisimulation theorem. Practically, this means:
- SHARES_MATH = equivalence-class membership (math-identity of atoms in same archetype class)
- A 1-step rewrite admits only the *identity isomorphism* between archetype-class members, not arbitrary substitution
- CHTV-1 verifier must confirm every resulting proof type-checks (sound by construction)

If soundness regresses, the cell HARD-FAILs and substrate-product positioning reframes to "substrate distinguishes equivalence-class organization (SHARES_MATH) from proof-step transitivity (DEPENDS_ON); LLMs conflate both."

## Composition with CELL-DEPTH-FORECAST (which you just shipped, HEAD ~ recent commit)

CELL-DEPTH-FORECAST validates the corpus-size-to-max-path scaling forecast (drill 2 Anchor 1).
Cell SMA-1 validates the depth-amplification-via-equivalence claim (drill 3).

Independent mechanisms:
- Forecast = WHAT depth substrate reaches at LANE B scale via corpus growth
- SMA-1 = WHAT depth substrate reaches NOW via amortization through equivalence relation

Both contribute to substrate-product positioning Section 5 (depth-trajectory + LLM categorical gap).

## Priority

After CELL-DEPTH-FORECAST completes + FINDER dual-report. Probably 1-2 cells away on Exp-Dev queue. If BATCH 19-26 ingest lands faster than Cell SMA-1 priority surfaces, P5_v1 + FINDER 2.5+ KPI take precedence.

If genuinely standing on Testbed ingest (no other ungated work), Cell SMA-1 is highest-value ungated next cell.

## Routing

- Exp-Dev: Cell SMA-1 priority after CELL-DEPTH-FORECAST + FINDER dual-report; ungated; CPU only ~30-60 min
- Research: standing for Cell SMA-1 verdict + Testbed status report + 3rd drill output already received (this handoff)
- Testbed: no direct action; URGENT 8-item list still standing

## Cross-references

- notes/research_DRILL_SHARES_MATH_amortization_depth_amplification_quantification_substrate_product_canonical_claim_extension_2026-06-13.md (drill 3 source)
- notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md (drill 2 source; companion to CELL-DEPTH-FORECAST)
- experiments/exp_substrate_depth_forecast_scalefree_hill_premise_cpu_v1.py (Exp-Dev CELL-DEPTH-FORECAST shipped)
- memory `substrate-L6-PROOF-FINDER-HARD-PASS-20-20-SOUND-axiom-terminating-38pct-genuine-T1-62pct-authoring-gap-USER-goal-deduction-closed-2026-06-13` (current L6-PROOF baseline)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2-of-5-paths-multi-mechanism-validated-2026-06-13` (KP P3 HARD_PASS gave 12 archetype classes; SMA-1 input)
