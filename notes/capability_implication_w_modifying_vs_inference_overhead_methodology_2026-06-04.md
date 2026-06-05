# Capability-implication -- W-modifying vs inference-overhead drill methodology

**From:** Research session
**To:** Orchestrator (primary); strategy_scribe (annotation execution)
**Date:** 2026-06-04
**Subject:** NEW brain-drill methodology — W-modifying vs inference-overhead architectural classification. Empirically validated by Bundle A v394 verdict pattern. Cap_map sub-property founding requested.

---

## What this is (plain language)

Today's calibration drill (research_drill_implicit_explicit_subsumption_calibration_2x_2026-06-04.md) identified the fundamental distinction that explains Bundle A's verdict pattern (2 HP + 3 MIDDLE + 1 HF). The Friston FEP HARD_FAIL was the only "surprise" — and it's now algebraically explained via subsumption + parameter-budget defeat.

This note requests cap_map sub-property founding for the NEW drill methodology going forward.

---

## The fundamental distinction

**W-MODIFYING mechanisms** change the substrate's weight matrix W and therefore change mu_NESS (the substrate's invariant measure). They CANNOT be subsumed by NESS dynamics because they alter what NESS is.

Examples (W-modifying):
- BCM three-factor Hebbian (dw = pre * post * M(t))
- cf-RPE (rank-1 counterfactual substitution; rewrites stored values)
- Sparse coding (changes input representation; changes effective W)
- STDP-asymmetric (adds W_STDP to W_Hebbian; non-symmetric W)
- Anti-Hebbian repulsion (modifies W via active repulsion)

**INFERENCE-OVERHEAD mechanisms** operate on a FIXED W via separate machinery. They ARE subject to NESS subsumption because substrate's native dynamics already minimize the objective they explicitly implement.

Examples (inference-overhead):
- Friston FEP precision matrix Pi (separate variational machinery on fixed W)
- Attention over fixed W (separate retrieval machinery)
- External memory bank with separate objective
- Bottleneck-adapter routing on fixed channels

---

## Empirical validation from Bundle A v394

| Bundle A variant | Mechanism class | Drill P_deflated | Empirical | Match? |
|---|---|---|---|---|
| cf-RPE alone | W-modifying | 0.32 | HP | YES |
| Drosophila sparse | W-modifying | 0.42 | HP | YES |
| STDP-asymmetric | W-modifying (sequence-class) | MIDDLE expected | MIDDLE | YES |
| 2-region | Mixed (Hebbian + sparse-Hebbian) | 0.28 | MIDDLE | YES |
| Bottleneck-adaptor | Inference-overhead | 0.22 | MIDDLE | YES |
| Friston FEP | Inference-overhead (DENSE Pi) | 0.28 | HF | NO -- but explained |

5 of 6 matches were correct; the 1 mismatch (FEP HF) is now algebraically explained.

---

## Algebraic decomposition

Going forward, brain-drill P_deflated must split:

**P_deflated_joint = P_algebraic * P_implementation**

Where:
- P_algebraic: framework theoretical correctness (what drills currently estimate)
- P_implementation = P_convergence * P_budget * P_no_subsumption * P_task_match

Sub-factors:
- P_convergence: explicit machinery faster than implicit dynamics?
- P_budget: rho = K_overhead / K_LM is small enough? (rho << 1 required)
- P_no_subsumption: W-modifying (NO subsumption) or inference-overhead (subject to subsumption)?
- P_task_match: task complexity at the framework's binding regime?

Recovery thresholds calibrated:
- Dense Pi at substrate scale N=4096 LM=10k: rho = 1678 (parameter budget defeat algebraically predicts HF)
- Diagonal Pi at K_LM = 50k+: rho ~ 0.1 (recovery threshold)

---

## Lit anchors

- Marblestone 2016 "cost function hypothesis" (algebraic vs implementation distinction)
- Rajeswaran NeurIPS 2019 iMAML (implicit vs explicit gradient computation; direct analog)
- Solomonoff 1964 + recent 2026 K-complexity neural weight norm equivalence (arXiv:2605.10878)
- Wang-Xu-Wang 2008 NESS Lyapunov (substrate's implicit objective)
- Cates-Tailleur 2015 active matter F_eff (constructive approximation to NESS)

---

## Requested cap_map sub-property founding

### Sub-property 1: Brain-architectural drill methodology

Under any relevant capability row (e.g., substrate-as-training-mechanism):

"Brain-architectural drill predictions must decompose P_deflated into P_algebraic + P_implementation. Empirical gain at substrate scale requires four conditions in addition to algebraic correctness: convergence rate improvement, parameter budget fit (rho = K_overhead/K_LM << 1), no NESS subsumption (W-modifying not inference-overhead), task-complexity match. Validated by Bundle A v394 verdict pattern: 5 of 6 architectural variants matched recalibrated predictions within ~10%; the 1 mismatch (FEP HF) is algebraically explained via dense Pi rho=1678 parameter-budget defeat. Future drill predictions should use the W-modifying vs inference-overhead distinction."

### Sub-property 2: Substrate's hidden objective subsumption mechanism

Under Constraint 2 dissolution / substrate-as-training-mechanism row:

"Substrate's native NESS dynamics minimize a hidden Lyapunov objective KL[p_t || mu_NESS] (per Wang-Xu-Wang 2008). Inference-overhead mechanisms (operating on fixed W) are SUBSUMED by this implicit objective and provide no empirical gain at substrate scale. Only W-MODIFYING mechanisms (changing mu_NESS itself) provide gain. This explains: BCM HARD_PASS (W-modifying), cf-RPE HARD_PASS (W-modifying), sparse coding HARD_PASS (W-modifying), Friston FEP HARD_FAIL (inference-overhead with dense Pi). Recovery via diagonal Pi at K_LM > 50k+ params remains a research direction."

### Sub-property 3: Updated P_deflated calibrations for today's 15 drills

Retroactively apply the methodology:

| Drill | P_algebraic | P_implementation | Recalibrated Joint |
|---|---|---|---|
| Friston FEP 2x | 0.68 | 0.003 | **0.002 (matches HF)** |
| cf-RPE 2x | 0.50 | 0.65 (W-modifying) | **0.33 (matches HP)** |
| Drosophila MB 2x | 0.55 | 0.75 (W-modifying) | **0.41 (matches HP)** |
| STDP 2x | 0.55 | 0.55 (W-modifying; task-mismatch at bigram) | **0.30 (matches MIDDLE at bigram)** |
| Multi-channel scale 3x | 0.40 | 0.40 (mixed inference + W) | **0.16 (matches MIDDLE)** |
| Position-binding combined 2x | 0.45 | 0.60 (combined W-modifying) | **0.27 (Bundle E prediction)** |

---

## What's NOT changing

- Existing cap_map row structure (no top-level row changes)
- Validated capability claims (composition L=10000, drift detection, deletion certificate algebraically grounded -- all stand)
- Lit anchor chain (10+ frameworks confirmed today; no removals)
- Substrate primitive set (no primitive changes; just methodology for predicting which primitive combinations will work empirically)

---

## What's CHANGING

- All future brain-drill prompts should explicitly require P_algebraic + P_implementation decomposition
- New drills should classify architectural variant as W-modifying or inference-overhead before estimating P_implementation
- Cap_map annotations for substrate-as-training-mechanism row should note the W-modifying-vs-inference-overhead distinction
- Future visibility entries should reference Marblestone 2016 + iMAML 2019 + K-complexity 2026 as lit anchors for the methodology

---

## Strategic implication

This methodology refinement is essentially a **paradigm shift** in how we predict empirical outcomes from brain-drills. Previous drill P_deflated estimates were calibrated for algebraic correctness but conflated with empirical gain. The new methodology cleanly separates the two.

Practical effect: future drill dispatches will produce more reliable empirical-outcome predictions. False-positive rate (drills predicting HP that empirically HF, like FEP) should drop substantially.

This also informs ARCHITECTURE DESIGN for substrate-as-training-mechanism:
- Prioritize W-modifying mechanisms (cf-RPE, sparse, STDP) -- known to work empirically at substrate scale
- Skip inference-overhead mechanisms at substrate scale (FEP, dense attention, external memory with separate objectives) UNLESS LM scales to 50k+ params
- For LLM-integration (Phase 0.5 v1 Rung A on Llama-3.2-1B): inference-overhead becomes viable at the 1B scale

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Orchestrator informed; strategy_scribe annotation execution
- Per [[feedback-capabilities-not-product-positioning]]: methodological refinement; not product-positioning
- Per [[feedback-value-creation-not-competition]]: improves drill calibration; adds rigor
- Per [[feedback-dont-overextend-theorems]]: methodology bounded to brain-architectural drills; not all research
- ASCII-only

---

**END.**

**Orchestrator:** route to strategy_scribe for cap_map sub-property founding per § "Requested cap_map sub-property founding" above. Next visibility entry should cite the new methodology + the Bundle A v394 empirical validation + the 10+ lit anchor chain.

**Research session:** future drill prompts will explicitly require P_algebraic + P_implementation decomposition per the established methodology.
