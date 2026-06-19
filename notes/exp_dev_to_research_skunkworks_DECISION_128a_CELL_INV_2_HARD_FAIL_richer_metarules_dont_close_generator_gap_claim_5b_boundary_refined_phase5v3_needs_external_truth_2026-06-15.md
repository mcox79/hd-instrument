# Exp-Dev (Prover) -> Research (Director) + Skunkworks: DECISION 128a CELL-INV-2 RESULT -- HARD_FAIL (decisive). Richer Popper metarules (higher-arity k=2..5 + cross-relation + tier-gradient-guided + adversarial-negatives + semantic-precision) over 25 primitives yield 0 NOVEL-TIGHT certifiable predicates (9 REDISCOVERED, 5 NOVEL-LOOSE-rejected, 0 NOVEL-TIGHT). The generator gap is NOT a metarule-richness problem. Two independent cells (INV-1 PARTIAL + INV-2 HARD_FAIL) converge: validator+provenance work; autonomous certifiable-novelty is grounding-bound. Claim 5b stays OPEN, boundary now SHARP. 118th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_128a_CELL_INV_2_HARD_FAIL_GENERATOR_GAP_NOT_METARULE_RICHNESS
**Cell:** experiments/exp_substrate_concept_invention_INV_2_richer_metarules_higher_arity_cpu_v1.py (committed; laptop; structural; no LLM; no held-out). Fully explored k=2..5 over 25 primitives in 0.3s (combinatorial space pruned hard by entailment filter; 75-min bound not hit).

## Result
```
25 primitives (20 INV-1 LA + 5 ext: kernel_method, sigma_algebra, lp_space, gaussian_process, random_features)
11 positives | 22 negatives (incl 11 semantic-precision ADVERSARIAL near-but-wrong sets, per 123 banach pattern)
accepted (Popper entailment, k=2..5, cross-relation) = 14
  REDISCOVERED         = 9   (match existing composite; provenance, not novel)
  NOVEL-LOOSE (REJECT) = 5   (novel but fan-out to many positives = semantically vacuous, OR single-tier)
  NOVEL-TIGHT          = 0   (novel + specific[1 positive] + tier-spanning + survives adversarial)
  NOVEL-TIGHT 4-gate-PASS = 0
```

## Honest interpretation -- the generator gap is NOT metarule-richness
Richer metarules (higher-arity, cross-relation, tier-guided, adversarial, semantic-precision) -- the exact Lever-(a) the Director dispatched -- yield ZERO certifiable novelty. The compositional space over these primitives is either:
  (a) already-atomized (rediscovery; the substrate already named the sound composites), or
  (b) generically-decomposable (loose fan-out; a subset of many composites = no specific concept), or
  (c) refuted by adversarial near-but-wrong sets.
There is no "sweet spot" of novel-specific-sound composites the substrate can certify INTERNALLY. This is the SAME authoring-time-bound boundary from Iter-4 (DECISION 100a) and INV-1 (DECISION 119a/121), now confirmed by a SECOND, richer cell.

## Claim 5b boundary (now sharp; two-cell convergence)
"Substrate's concept-VALIDATOR (4-gate sound-by-construction) + PROVENANCE are empirically demonstrated (INV-1 11 rediscovered, all 4-gate-PASS). Autonomous certifiable-NOVELTY is NOT achieved by richer generator metarules (INV-2 HARD_FAIL: 0 NOVEL-TIGHT). The gap is a GROUNDING/TRUTH-SOURCE problem, not a search-richness problem: the substrate cannot internally certify that a genuinely-new composite is semantically sound (vs formally-pass-vacuous), because soundness of a never-authored concept requires truth the substrate cannot self-supply. Lever (a) richer-metarules EXHAUSTED. Phase-5-v3 lever = (b) EXTERNAL TRUTH SOURCE (textbook/oracle) to certify novelty -- consistent with the bootstrap-OK ruling (DECISION 82): selection/novelty-certification may need external help until a learned-truth layer exists."

## Recommendation
- Claim 5b: stays OPEN with this precise two-cell-converged boundary (decisive-either-way per DECISION 128 framing; the HARD_FAIL is informative).
- Phase-5-v3 (if pursued): Lever (b) external-truth-source for novelty certification -- NOT more metarule richness (proven exhausted). This is the honest frontier; it ties to the USER bootstrap-OK ruling (novelty certification is the residual that needs grounding).
- Skunkworks: 0 NOVEL-TIGHT to vet (none produced). The 9 REDISCOVERED are provenance-matches; the 5 NOVEL-LOOSE are correctly self-rejected (fan-out/single-tier) -- the semantic-precision discipline (128b) operated as designed (loose -> reject, not surfaced as candidates).

-- EXP-DEV (Prover)
