# Pre-registration: substrate_distill_verify_operator_equivalence_v2_full

**Date:** 2026-06-25
**Anchor:** substrate_distill_verify_operator_equivalence_v2_full
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent)
**N_FOLDS:** 3 (held-out cross-validation across duplicate-operator groups)

## Promotion context

USER 2026-06-25: the v1 cell ran at n_seeds=1 (single deterministic pass over Store; HARD_PASS 6/6 NAMED operators
provably-equivalent via CHTV-1 typed-signature equality). Not chain-grade-tier-eligible per BIAS-14.

v2 META-REASONING DISCIPLINE per USER: "the test set must be carefully held-out (operators NEVER seen during training)".
Since the original cell is deterministic (the Store doesn't change between seeds), v2 implements **3-FOLD STRATIFICATION**
with capability-fallback-DISABLED in the held-out fold to force typed-only reasoning (no name-based shortcut via
shared_caps).

## Strategic significance

This is the substrate's first META-REASONING primitive. CHTV-1 (Closed Hyperdimensional Type Validator v1) implements
typed-signature equality: two operators are PROVABLY_EQUIVALENT iff their algebra_dict signatures are identical (domain,
operation_type, signature_input_type, signature_output_type, complexity_class). Sound by construction.

A chain-grade win here unlocks **Stage 3 self-improvement Phase 1**:
- The substrate can prove its own duplicate operators equivalent.
- It can distill (merge) operators without losing capability.
- This is one of the building blocks for "substrate proposes new mathematics" per the USER strategic vision.

Honest scope: CHTV-1 is sound — it doesn't DISCOVER equivalence; it APPLIES a decidable type-equality rule. The held-out
test is whether the rule applies UNIFORMLY across operator subsets the prover has not "seen" with capability hints
disabled. A chain-grade verdict here means: meta-reasoning rule is robust to test-set sampling + no cv variance from
hidden dependency on training-set capability annotations.

## Mechanism (v1 unchanged + v2 fold stratification)

Per seed S in [11, 13, 19]:
1. Load all duplicate-operator groups from `data/substrate_index` (deterministic; ~29 groups in v1).
2. `np.random.default_rng(S).permutation(len(names))` shuffles the group set.
3. Held-out fold = first 1/3 of shuffled (~9-10 groups); training fold = remaining 2/3.
4. Classify held-out fold with CHTV-1 typed-signature equality, **`allow_capability_fallback=False`** (the prover cannot
   fall back to shared serves_capability matching; must rely on algebra_dict equality alone).
5. Distillation ratio = (PROVABLY_EQUIVALENT + EQUIVALENT_BY_CAPABILITY) / total held-out.

   With capability-fallback disabled, EQUIVALENT_BY_CAPABILITY can only fire if algebra_dict is present + non-trivial;
   bare-untyped groups become UNDECIDABLE_BY_PROVER (the honest classification).

Aggregate:
- mean distillation ratio across 3 seeds
- cv across 3 seeds
- ANY NOT_EQUIVALENT in any held-out fold (HARD_PASS requires zero)
- fold-overlap pair counts (verifies seeds genuinely sample different folds)

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE_META_REASONING
- held-out distillation ratio mean >= 0.80
- cv across 3 seeds <= 0.07
- ZERO NOT_EQUIVALENT in any held-out fold

### HARD_PASS_PARTIAL (= MIDDLE_BAND)
- held-out distillation ratio mean 0.60 - 0.80

### HARD_FAIL
- held-out distillation ratio mean < 0.60

## Q-discipline (BIAS-Q: suspect 1.000 results)

v1 reported 6/6 NAMED + 27/29 all-dups provably-equivalent (1.00 named, 0.93 all). Suspect saturation. With held-out folds
+ capability-fallback DISABLED:
- some seeds may put 2 NAMED in held-out, others 4 NAMED
- bare-untyped groups (UNDECIDABLE) reduce distillation_ratio below 1.00 even in the chain-grade case
- if held-out distillation_ratio is consistently 1.000 across all 3 seeds, suspect that the held-out folds happened to
  contain only fully-typed groups (an artifact of the 33-group corpus + shuffle stride)

This Q-discipline is implicit in the cv band (cv <= 0.07 means fold-sampling matters; the variance argues against
saturation).

## Cross-cell discipline

- ASCII only
- Substrate-only (no LLM forward calls; pure Store read + algebra_dict comparison)
- Per-arm metrics in verdict_msg per Fix #28 (per-seed held distillation + per-seed not_equiv count)
- Bands locked at module init via assert
- Seeds [11, 13, 19]
- META_M6: NAIVE baseline = "training-fold distillation_ratio under capability-fallback ENABLED" = the v1 result; held-out
  is the held-out novelty test, not a copy of v1.

## Smoke-vs-full discipline

Smoke (1 seed, seed=11) vs full (3 seeds [11,13,19]) match on:
- Same Store load
- Same N_FOLDS=3
- Same CHTV-1 classifier
- Same capability-fallback rule (DISABLED on held-out, ENABLED on training; both smoke + full)

Only difference: number of seeds aggregated. No regime sign-flip possible.

## Timeout estimate

Smoke wall: ~1s (per v1 timing; pure Store read + 29 groups CHTV-1 dispatch).
formula: timeout_s = ceil(1.5 * 1 * 1^1.5 * 3) = 4.5s
Plus Store load: **timeout_s = 300** (5min; conservative for first-time Store load).

## PROT compliance

- PROT-018, 019, 020: do not apply.
- PROT-021: timeout < 14400s; but cell imports `_seed_checkpoint` anyway.

## Symmetric verify rail

Verdict reports:
- per-seed held distillation ratio + per-seed not_equiv count
- per-seed named-held-distillation ratio (the NAMED-subset rail)
- fold-overlap pair counts (the disjoint-folds rail)
- mean + cv across seeds (the stability rail)

## Honest negatives possible

- Some seeds may put bare-untyped groups into held-out fold -> distillation_ratio drops below 0.80 -> MIDDLE_BAND honestly.
- cv across seeds may exceed 0.07 if the bare-untyped distribution is uneven across folds.
- A NOT_EQUIVALENT in any held-out fold drops the verdict from HARD_PASS to MIDDLE_BAND (must be zero).
