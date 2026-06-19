# Routing -- Training-speed iterative optimization ladder: STAGE A (tiny char-LM)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + Testbed (Testbed for later cloud stages)
**Date:** 2026-06-04
**Type:** Empirical training-speed optimization campaign (Stage A; tiny char-LM scale)
**Source:** User strategic direction 2026-06-04: "show max training on tiny models, move up one tier of LLM size, repeat and optimize"

---

## The strategic framing

**Iterative training-speed ladder:** at each tier of LLM size, train as fast as possible using ALL substrate tricks accumulated + develop new ones at that tier. Move up one tier. Repeat. Measure training-speed advantage vs standard baseline at each tier.

**Constraints:**
- Keep runs SHORT (no multi-hour cloud tests)
- Cumulative trick library compounds at each tier
- Optimize aggressively before moving up

**Stages:**
- Stage A (THIS ROUTING): tiny char-LM (substrate-class; CPU/remote 4060 Ti; $0)
- Stage B (conditional): Pythia-160M class (remote 4060 Ti; $0; ~30-60 min)
- Stage C (conditional): Llama-3.2-1B class (remote 4060 Ti if 8GB fits, else cheap cloud H100 < 1h)
- Stage D (conditional): Llama-3.1-8B class (cloud H100; < 1h; ~$5-10)

Each stage conditional on prior HP. Keep all individual runs < 1h.

---

## Stage A capability question

What's the FASTEST we can train a tiny char-LM (V=70-512, K=2-4 context) using substrate's full architecture stack at substrate-class N=4096-8192, and what's the wall-time speedup vs standard char-LM transformer baseline at matched task performance?

This validates substrate's training-speed claim (~10^5x per-sample + 80-95x hierarchical wall-time per training-speed drill) at smallest scale BEFORE scaling up.

---

## Trick library to apply at Stage A

Per today's research drills + empirical landings:

**W-modifying primitives (HP at Bundle A):**
- cf-RPE (counterfactual rank-1 substitution)
- Drosophila sparse coding (f=0.05)
- STDP-asymmetric (sequence storage)

**Heterogeneous pairings (predicted superadditive per shared-axis drill):**
- cf-RPE + STDP-asymmetric (task + temporal)
- cf-RPE + position-binding (task + temporal)

**Empirically-validated trigram architecture (Bundle E HP):**
- Position-binding + symmetric Hebbian (E1 HP at trigram)
- Position-binding + STDP (E2 HP at trigram)

**Extended capacity (per resonator capacity drill):**
- Sparse resonator extension (K=26 published precedent)
- Noise-injection extension (50x free)

**Hierarchical aggregation (5-corpus HP):**
- Many parallel sub-substrates + meta-aggregator
- Multiplicative capacity at orthogonal domain keys

**Operating modes:**
- Iterated retrieval (Mode 4; NC1)
- Adaptive composition (Mode 2; Turing class)

---

## Pre-reg HP/MID/HF for Stage A

**Anchor:** `substrate_training_speed_stage_a_tiny_charLM_all_tricks_v1_n8192`

**Cells:**

### Cell A-baseline: Standard char-LM transformer at matched task

- 4-layer character-LM transformer
- Wikitext-2 character-level corpus (~10MB; standard char-LM benchmark)
- Train to convergence (target BPC per literature)
- Measure: wall-time to target BPC; per-sample compute
- Pure-gradient backprop standard training

### Cell A-substrate-minimal: Substrate-hybrid minimal architecture

- Substrate-Hebbian-attention layers (DeltaNet-class delta-rule)
- Gradient-trained output head only
- Same Wikitext-2 character corpus
- Train to same target BPC
- Measure: wall-time to target BPC; per-sample compute
- Compare to A-baseline: SPEEDUP FACTOR primary metric

### Cell A-substrate-all-tricks: Substrate-hybrid with full trick library

- Substrate-Hebbian-attention + cf-RPE + Drosophila sparse + STDP-asymmetric + position-binding + modern Hopfield p=4
- Gradient-trained output head
- Same task
- Measure: wall-time to target BPC
- Compare to A-baseline: SPEEDUP FACTOR primary metric

### Optional Cell A-hierarchical: Substrate-hybrid + hierarchical aggregator

- 3-5 parallel sub-substrate-LMs (each on different corpus subset)
- Substrate aggregator + meta-output head
- Same task
- Measure: wall-time advantage from parallelism

**Pre-reg:**

- **HARD-PASS:** A-substrate-all-tricks achieves target BPC at < 0.1x wall-time of A-baseline (10x speedup) AND BPC within 20% of baseline final
- **MIDDLE:** 2-10x speedup OR BPC degraded but speedup > 50x
- **HARD-FAIL:** speedup < 2x (substrate provides no meaningful training-speed advantage at this scale)

## Resource

Local CPU + remote 4060 Ti (no cloud at Stage A)

## Cost ceiling

$0. Per-cell wall < 1h (target). Total Stage A wall: ~3-4h across all cells (run in parallel where possible).

## P_deflated (per today's methodology)

**P_algebraic for HP = 0.75**: substrate's algebraic training-speed advantage is well-grounded (10^5x per-sample ops; DeltaNet 50% speedup published precedent at 1.3B)

**P_implementation:**
- P_convergence = 0.55 (multiple architectures interacting; harder to converge cleanly)
- P_budget = 0.85 (tiny model fits substrate-class easily)
- P_no_subsumption = 0.90 (W-modifying)
- P_task_match = 0.65 (char-LM at tiny scale is well-validated empirically today)
- Joint P_implementation ~ 0.27

**P_joint = 0.75 * 0.27 ~ 0.20 for 10x speedup HP**

Plus higher P (~0.40) for 2-10x speedup (MIDDLE-band).

## Engineering scope

~4-6h:
- Wikitext-2 char-LM corpus + tokenization (reuse if exists)
- Standard char-LM transformer baseline (~2h; standard scaffolding)
- Substrate-Hebbian-attention layer (DeltaNet-class; ~2h; reuse Bundle E E1 scaffold)
- Full trick library integration (~2h; integrate Bundle A + Bundle E + other validated primitives)
- Wall-time measurement infrastructure (~30 min)
- Comparison + speedup factor calculation (~30 min)

## Strategic outcome

### If A-substrate-all-tricks HP at 10x+ speedup

- Substrate's training-speed advantage EMPIRICALLY ANCHORED at tiny scale
- Documents the trick library that produces 10x+ speedup
- DISPATCH STAGE B (Pythia-160M class with all-tricks + develop new ones)
- Product narrative: "substrate trains 10x+ faster than transformer at tiny LM scale" empirically validated

### If A-substrate-all-tricks MIDDLE (2-10x speedup)

- Substantial but not transformative speedup
- Document which tricks contribute most
- Stage B with reduced speedup target (5x?)

### If A-substrate-all-tricks HF (<2x speedup)

- Substrate's training-speed claim refuted at tiny scale
- Identify why: convergence issues? trick conflicts? task mismatch?
- Reassess training-speed product narrative
- DO NOT proceed to Stage B until Stage A iteration produces real speedup

---

## What this is (plain language)

Take a tiny character-language-model (~10MB Wikitext-2). Train it three ways:

1. Standard transformer (the baseline; how fast is the comparison?)
2. Substrate-hybrid minimal (just DeltaNet-class substrate-Hebbian-attention)
3. Substrate-hybrid with ALL tricks (cf-RPE + sparse + STDP + position-binding + modern Hopfield + hierarchical)

Measure wall-time to reach same final BPC. Compute speedup factor.

If substrate is 10x+ faster: validates the training-speed claim. Move up one tier.

If not 10x+: figure out which tricks are working vs not. Iterate at this tier before moving up.

---

## Future stages (conditional)

### Stage B: Pythia-160M class small LLM (CONDITIONAL on Stage A HP)

- Apply ALL Stage A tricks at Pythia-160M scale
- Develop new tricks specific to 160M class (e.g., layer-wise progressive training; attention-mask optimization)
- Same SPEEDUP FACTOR vs standard Pythia-160M training
- Target: 10x+ speedup (same threshold; or relax to 5x if Stage A showed marginal speedup)
- Resource: remote 4060 Ti ($0); wall < 1h
- Routing: new file when Stage A lands

### Stage C: Llama-3.2-1B class (CONDITIONAL on Stage B HP)

- Apply Stages A+B tricks + new ones for 1B class
- Target: 10x+ speedup vs standard Llama-3.2-1B training
- Resource: remote 4060 Ti (8GB fits 1B model; per Phase 0.5 v1 Rung A precedent); wall < 1h
- $0 if fits remote; otherwise cheap cloud H100 < 1h ~ $5

### Stage D: Llama-3.1-8B class (CONDITIONAL on Stage C HP)

- Apply Stages A+B+C tricks + new ones for 8B class
- Target: 10x+ speedup vs standard Llama-3.1-8B training
- Resource: cloud H100; wall < 1h ~ $5-10
- Per user: keep cloud SHORT; iterate aggressively

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed; Testbed informed for later cloud stages
- Per [[feedback-cloud-only-when-absolutely-necessary]]: Stage A is $0; Stages B-C strive for $0; Stage D only if 8B requires cloud
- Per [[feedback-small-scale-first-methodology]]: Stage A at substrate-class; ladder up rungs in tight iterations
- Per [[feedback-short-cloud-runs-preferred]]: all stages target < 1h wall per individual run
- Per [[feedback-no-padding-experiments]]: cells are minimum to discriminate training-speed claim
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF pre-reg with specific speedup thresholds
- Per [[feedback-pressure-test-negative-findings]]: if Stage A HF, drill on WHY (don't accept "substrate cannot speed up training" without pressure-testing alternate modes)
- ASCII-only

PROT-018: anchor uses `_n8192_v1` suffix
PROT-021: source=local CPU + remote 4060 Ti, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** Stage A is ~4-6h engineering + ~3-4h experiment wall total. $0 (local CPU + remote 4060 Ti). Reuses Bundle A + Bundle E + DeltaNet scaffolds. Verdict drives Stage B dispatch + training-speed product narrative empirical validation.

**Orchestrator + Testbed:** informed. Stages B-C-D conditional on Stage A. Cap_map updates pending each stage outcome.

**Research session:** holds for Stage A verdict + cornerstone audit C1/C2/C3 verdict (separate Testbed routing); when both land, ship consolidated capability-implication note on substrate's training-speed + audit-at-frontier empirical anchors.
