# Routing -- K=3 synthetic-uniform V=70 Zipf falsifier test

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical Zipf-mechanism falsifier (1 cell + 1 reference; CPU)
**Source:** Position-binding symmetric W trigram explanation 2x drill landed 2026-06-04 (research_drill_position_binding_symmetric_w_trigram_explanation_2x)

---

## Capability question

Does substrate's K=3 trigram HP at V=70 N=4096 (Bundle E E1; +1.291 nats; 3/3 seeds) come from natural-language Zipf demand-deflation, or does it persist at synthetic uniform-random vocabulary?

Per today's drill: corrected K*_corr ~ 3.97 explanation has THREE compounding factors:
1. Heteroassociative beta~4 multiplier
2. Zipf demand deflation (V^2=4900 → ~150 active contexts)
3. Language redundancy rho~0.43 (V_eff ~ 13.5)

This test directly validates whether Zipf is LOAD-BEARING. If synthetic uniform fails: Zipf is essential. If synthetic uniform also passes: Zipf is not load-bearing (heteroassociative beta is the main driver).

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096`

**Cell U1:** Position-binding + symmetric Hebbian at K=3 trigram with SYNTHETIC UNIFORM-RANDOM V=70 corpus at N=4096, 5 seeds

Reference: Bundle E E1 (natural-language V=70 char-LM trigram at N=4096): gap +1.291 nats, 3/3 seeds, HARD_PASS

**Pre-reg per drill prediction:**

- **HARD-FAIL (Zipf load-bearing):** synthetic gap < 0.5 nats AND <= 1/5 seeds converge. Confirms Zipf is essential mechanism.
- **MIDDLE (partial Zipf effect):** synthetic gap in [0.5, 0.8] nats. Zipf provides ~half the gain.
- **HARD-PASS (Zipf NOT load-bearing):** synthetic gap > 0.8 nats AND 4/5 seeds. Refutes Zipf hypothesis; heteroassociative beta drives K*_corr extension on its own.

## Resource

Local CPU. Reuses Bundle E scaffolds for position-binding + symmetric W.

## Cost ceiling

$0 CPU. Per-seed wall ~60-90s. Total ~5-10 min for 5 measurements.

## P_deflated (per today's methodology)

**P_algebraic_HF (Zipf load-bearing) = 0.70**: drill identifies Zipf as one of three compounding factors; synthetic uniform should fail substantially per algebraic analysis

**P_implementation_HF:**
- P_convergence: 0.85 (uniform corpus is well-defined statistical task)
- P_budget: 0.90 (N=4096 fits comfortably)
- P_no_subsumption: 0.95 (W-modifying)
- P_task_match: 0.65 (uniform corpus is THE NULL test of Zipf hypothesis)
- Joint P_implementation_HF ~ 0.47

**P_joint_HF = 0.70 * 0.47 ~ 0.33 for HARD-FAIL**

Plus complementary P_joint_HP (Zipf NOT load-bearing) ~ 0.20: if HP, Zipf-deflation hypothesis refuted but heteroassociative beta still explains E1 HP.

The test is INFORMATIVE either way: HF confirms Zipf is essential; HP refines the algebraic story to heteroassociative beta + redundancy alone.

## Engineering scope

~30-60 min:
- Synthetic uniform-random V=70 corpus generator (~10 min)
- 5-seed eval at K=3 trigram with position-binding + symmetric W (reuses Bundle E E1 scaffold)
- Comparison to E1 natural-language baseline

Reuses Bundle E scaffolds substantially.

## Strategic outcome

### If HF (synthetic gap < 0.5; Zipf load-bearing)

- Confirms Zipf demand-deflation is essential for substrate's K=3 trigram capability at substrate-class N
- Refines corrected K*_corr formula: V_eff term is necessary; natural-language structure is load-bearing
- Predicts: synthetic harder-task experiments will fail; natural-language Shakespeare should work
- Cap_map: founding for "substrate K* extension on natural language requires V_eff << V"

### If MIDDLE (synthetic gap 0.5-0.8)

- Zipf provides partial gain; heteroassociative + redundancy provide rest
- Multi-mechanism story confirmed; no single mechanism dominates

### If HP (synthetic gap > 0.8; Zipf NOT load-bearing)

- Heteroassociative beta + redundancy account for E1 HP without Zipf
- Substrate's K*_corr extends to synthetic uniform tasks (broader than predicted)
- MAJOR finding: substrate's K=3 capability is more general than natural-language-only
- Bundle G synthetic K=8-16 extended-context predictions strengthen

---

## What this is (plain language)

Today's drill identified THREE mechanisms explaining substrate's HP at trigram:
1. Heteroassociation gives beta=4 capacity multiplier
2. Zipf in natural language deflates demand by ~30x
3. Language redundancy lowers effective vocab

The Bundle E E1 result used real natural language (Zipf statistics + redundancy). This test uses SYNTHETIC UNIFORM-RANDOM corpus (no Zipf, no redundancy). If substrate still passes: Zipf and redundancy aren't necessary; heteroassociation alone explains the result. If substrate fails: Zipf and/or redundancy are essential.

This is a clean MECHANISM test. Single cell; ~10 min; $0.

---

## Strategic context

Connects to:
1. Position-binding symmetric W trigram explanation 2x drill (landed; predicted this test)
2. Bundle E E1 (HP at natural-language trigram)
3. True task-complexity scaling law drill (landed; identifies V_eff as binding)

If HF: substrate's K* extension is natural-language-specific; need V_eff << V to be load-bearing.
If HP: substrate's K* extension generalizes beyond natural language; broader product narrative.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: single load-bearing cell with clear mechanism falsifier
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-pressure-test-negative-findings]]: tests whether Zipf claim is operating-condition-specific
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** small ~5-10 min CPU test once engineered (~30-60 min). Verdict drives Zipf-mechanism validation + K*_corr formula refinement.
